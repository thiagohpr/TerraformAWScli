# Roteiro

> ### Sumário
 - Instalação das Dependências
 - Roteiro de Aplicação
>

## Instalação
### Python
Antes de começar a Implementação, é necessário configurar o ambiente de desenvolvimento. 

O ambiente interativo foi desenvolvido em **Python**.

**Bibliotecas necessárias:**

>* subprocess
>
>   Possibilitará rodar comandos `terraform` a partir da programação em Python.
>

>* json
>
>    Ler arquivos .json apropriadamente. 
>

>* re
>
>    Expressões regulares, para identificar padrões nos arquivos de modelo. Serão explicados mais adiante no roteiro.
>

### Terraform

O terminal deverá reconhecer o comando `terraform`. Para isso, baixe o [arquivo binário do compilador](https://developer.hashicorp.com/terraform/downloads). Ele deverá ser configurado no PATH do computador:
1. Descompacte o arquivo e mova para um diretório apropriado (no meu caso, criei uma pasta `terraform` dentro dos `Arquivos de Programas`).
2. Abra o Painel de Controle > Sistema e Segurança > Sistema > Configurações avançadas do sistema > Variáveis de Ambiente
3. Seleciona `PATH` edite e adicione o caminho da Pasta em que o binário extraído está.

Após esse procedimento, o terminal deverá ser capaz de entender o comando `terraform`.

    CheckPoint-1

    1. Digite `terraform -help` no terminal e analise a resposta.
    2. Se necessário, refaça os passos anteriores.

### AWS

A infraestrutura de rede administrada pelo terraform deverá ser postada na AWS e, para que o terraform identifique o IAM User, há muitas formas de cadastrá-lo. É possível passar diretamente as chaves no main.tf, mas por questões de segurança de chaves e praticidade, esse projeto utilizou o método da AWS CLI para criar um perfil e associar as chaves ao Terraform.

**Instalar a Interface de Comando da AWS**
1. Baixe e rode o [instalador](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html). 
2. `aws configure --profile "nome_perfil"`
3. Preencha com suas credenciais e com o Output em `json`.

Com os módulos em python, os comandos `terraform` indentificáveis e as credenciais registradas, é possívvel começar a implementação.

## Aplicação

### Insfraestrutura mínima do Terraform

Antes de pensar em automatizar a criação ou remoção de recursos em python, é necessário configurar um arquivo mínimo .tf para que o `terraform init` identifique um projeto e o provedor AWS. Além disso, criar uma `VPC` e uma `subrede` para que o usuário possa alocar seus recursos.

1. Dentro de uma pasta `terraform`, crie o `main.tf`, que será responsável pro alocar os rescuros mínimos.
2. Crie os bloco `terraform`, com a versão baixada anteriormente, `provider "aws"` com o nome do `profile` sendo aquele registrado anteriormente no AWS CLI.
3. Pesquise como você poderia criar, pelo terraform, uma virtual Private Cloud e uma sub rede associada a ela. Adicione os blocos ao `main.tf`.

### Projeto em Python

Pensando na grande motivação de automatizar a criação de recursos, bem como deletá-los, é possível rascunhar o que o `main.py` deverá fazer em sua execução. 

 - `terraform init`
 - Perguntar ao usuário qual ação deverá ser tomada.
    * Criar recurso
    * Deletar recurso
    * Deletar todos os recursos
    * Listar recursos administrados pelo terraform
    * Sair do programa
 - Executar o bloco de código correspondente a essa ação. 
 - Se a resposta não for sair, fazer a pergunta novamente. Se for, parar a execução.

1. Crie o arquivo `main.py` e implmente a máquina de estados representada acima.
2. Por enquanto ignore os blocos específicos de código para cada ação, foque apenas na interação do usuário.
3. Pesquise como utilizar a biblioteca `subprocess` para rodar o comando `terraform init` dentro da pasta `terraform` criada anteriormente. Faça o programa esperar pela execução completa do comando antes de perguntar ao usuário a ação.

    Checkpoint-2

    1. Rode o programa, teste se as ações estão caindo em blocos diferentes de código.
    2. Verifique se dentro da pasta `terraform` foi criado um tf.state do projeto.



### Criar um Recurso
O terraform aplica uma mudança na infraestrutura se perceber que houve alguma mudança na pasta em que o `terraform init` foi executado. É possível fazer uma relação com o jeito em que o GitHub opera, identificando mudanças desde de o último `commit` e `push`.

    Checkpoint-3

    1. Quais os comandos equivalentes do commit e push para um projeto em Terraform?
    2. Dessa forma, qual seria uma forma de subir uma instância na AWS sabendo que o terraform identifica mudanças no projeto?

Dessa forma, o fluxo de operações para criar qualquer recurso é:

* Perguntar ao usuário qual recurso será criado.
* Verificar quantos arquivos daquele recurso já existem.
* Criar um arquivo .tf único para o novo recurso.
* Fazer o usuário preencher todas as variáveis daquele recurso. Deverá haver um controle de quais variáveis são importantes para cada recurso.
* Escrever nos arquivos de variável os novos valores, em um formato que o terraform entenda.
* terraform plan e terraform apply.

Algumas problemáticas no desenvolvimento da função para criar um recurso.
1. Cada recurso tem um formato específico e variáveis específicas.
2. Deve haver um mecanismo para diferenciar os arquivos, as variáveis e os nomes de recursos do mesmo tipo.

    Checkpoint-4

    Pense em uma solução para cada problema acima. Não há apenas um jeito de tratar recursos e variáveis novas. Se quiser saber como foi implementado nesse projeto, continue a leitura.

Soluções:
1. Arquivos .txt modelos, para que o main.py copie os blocos específicos de cada recurso. Por exemplo: 

`instance.txt`
```
resource "aws_instance" name_tf {
  ami           = var.instance_ami
  instance_type = var.instance_type
  subnet_id = aws_subnet.main_subnet.id
  vpc_security_group_ids = [var.sg_id]
}
```

2. Utilizar um contador de recursos iguais e criar se não houver um arquivo daquele contador. Por exemplo, se o projeto já possui uma instance0.tf, ele deve criar o instance1.tf. As variáveis são tratadas do mesmo jeito (instance_ami0, intance_ami1, etc.)


Considerando o fluxo de operações, já é possível implementar uma lógica para criar um recurso. Use e abuse da função **open** do python e cuidado com os paths de cada arquivo.

*Dica: Não tenha medo de testar várias vezes, basta não rodar o terraform apply para manter-se num ambiente de desenvolvimento.*

### Deletar um Recurso Específico
Sabendo que o padrão anterior de criação está funcional, deletar um recurso pode ser bem mais trivial do que elaborar uma lógica de criação.

* Listar todos os recursos sendo administrados pelo terraform ao usuário.
* Perguntar qual será deletado.
* Deletar o arquivo .tf do recurso.
* Apagar apenas as variáveis daquele recurso do variables.tf.
* terraform plan e terraform apply

Dessas etapas, a que precisa de um cuidado maior é a de reescrever o variables.tf. No entanto, se a diferenciação de variáveis pelo índice de contagem explicada anteriormente está funcional, isso não deverá ser um problema.

### Deletar Todos os Recursos
Esse bloco de código é o mais simples, já que o próprio terraform tem um comando que deleta toda a infraestrutura que identifica estar sendo gerenciada por ele. No entanto, ele não é a única etapa.

    Checkpoint-5

    O que aconteceria se o main.py apenas rodasse o comando terraform destroy?

Pense no que foi feito na infraestrutura local para deletar um recurso específico e implemente esse bloco de código.

### Listar Recursos
Novamente, codificar essa parte é fácil sabendo que o próprio terraform tem um arquivo que armazena os recursos geridos. Dessa form, basta entender como os recursos são listados e printar ao usuário informações importantes.

## Conclusão
Explicar a implementação desse projeto é algo importante poque foi feito com muito mais lógica em python do que com ferramentas em terraform, mesmo que se baseie em comportamento dele. Espero que, ao final desse roteiro, todas as funções criadas em python estejam claras e que seja possível replicar este projeto. Sinta-se livre para explorar os arquivos prontos e rodar no seu computador, prestando sempre atenção nos requisitos já explicados para o funcionamento.
