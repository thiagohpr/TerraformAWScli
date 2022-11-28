# Projeto de CLI para Terraform com Provider AWS
Thiago Hampl de Pierri Rocha

Projeto final para a Disciplina de Computação em Nuvem - Insper

Leia o arquivo roteiro.md desse repositório! Lá estão as dependências do projeto, etapas de configuração do ambiente e instruções de implementação. Aqui estão apenas as instruções de uso.

## Roteiro de Uso

Rodando o `main.py`, o terminal irá ao perguntar ao usuário 5 opções, cada uma delas interligadas com uma funcionalidade útil para gerir infraestrutura de rede.

0. Criar um Recurso
    * Instância
        * Sistema Operacional (default: Ubuntu Server 18.04)
        * Tipo de Instância (default: t2.micro)
        * Associar a algum security group
    * Security Group
        * Nome
        * Portas de entrada (default: 22)
        * Protocolo de entrada (default: tcp)
1. Deletar um recurso específico
2. Deletar toda a infraestrutura gerida pelo Terraform
3. Listar infraestrutura gerida pelo Terraform
4. Parar execução do Programa

Para acessar cada recurso, basta digitar o número da ação ao rodar o programa. Para as variáveis com valor Default, o programa irá dar a opção de apenas apertar enter (responder vazio) para que o Default seja aplicado. Para as variáveis sem um valor específico, o programa irá obrigar o preenchimento.

No caso de criar um Security Group, tome cuidado pois a AWS pede um nome único em toda a nuvem. O programa Python local não verifica isso e, por isso, ao criar um nome seja bastante específico e dê um nome que com certeza não exista. Não economize caracteres.
