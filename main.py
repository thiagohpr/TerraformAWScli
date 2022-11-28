from subprocess import run, Popen
import os
import json
import re


path = os.getcwd().replace('\\','/') + "/terraform"


#Cria um arquivo .tf do resource a ser criado, na pasta terraform
#Retorna as variáveis a serem preenchidas pelo usuário
def write(resource):
    resource_path = f'{resource}.txt'
    with open(resource_path, 'r') as f:
        resource_model = f.read()

    with open('resources.json', 'r') as json_file:
        variables = json.load(json_file)[resource]

    new_file = False
    i=0
    while new_file == False:
        file_path = f'{path}/{resource}{i}.tf'
        if os.path.isfile(file_path)==False:
            new_file = True
            resource_model = resource_model.replace("name_tf",f'"{resource}{i}"')
            for v_obj in variables:
                for v in v_obj.keys():
                    resource_model = resource_model.replace(f'var.{v}',f'var.{v}{i}')
        i+=1
    with open(file_path, 'w') as f:
        f.write(resource_model)
    return i-1, variables


#Bloco de criação de recurso
def create_resource():
    #Perguntar ao usuário o Recurso e criar o arquivo
    dic_sg = list_sg_ids()
    resources = ['security_group', 'instance']
    for i, r in enumerate(resources):
        print(f'{r} => {i}')
    
    ask_resource = True
    while ask_resource:
        resource_id = int(input("-- "))
        if resource_id>=0 and resource_id<len(resources):
            if len(dic_sg) == 0 and resource_id==1:
                print("Para criar uma instância é necessário antes criar um Security Group!")
            else:
                ask_resource = False
    resource_i, variables = write(resources[resource_id])
    #------

    #Preencher todas as variáveis do recurso
    dic_var = {}
    print("Preencha os valores dos parâmetros:")
    print("Enter para Default")
    print('\n')
    for var_obj in variables:
        for var_name, default_obj in var_obj.items():
            default = default_obj['default']
            if default!='Null':
                if 'default_nickname' in default_obj.keys():
                    default_nickname = default_obj['default_nickname']
                    resp = input (f'{var_name} (default = {default_nickname}):   ')
                else:
                    resp = input (f'{var_name} (default = {default}):   ')
                if resp=='':
                    dic_var[var_name] = default
                    break
            elif var_name=="sg_id":
                print("Atribua um Security Group à Instância: ")
                for i,sg_name in enumerate(dic_sg.keys()):
                    print(f'{sg_name} => {i}')

                ask_resource = True
                while ask_resource:
                    sg_resp = int(input("-- "))
                    if sg_resp>=0 and sg_resp<len(dic_sg):
                        ask_resource = False

                sg_values = list(dic_sg.values())
                resp = sg_values[sg_resp]

            else:
                valid_answer = False
                while valid_answer == False:
                    resp = input (f'{var_name} (obrigatório):   ')
                    if resp!='':
                        valid_answer = True
                    else:
                        print('Esse parâmetro é obrigatório.')
            dic_var[var_name] = resp
    #-----

    #Para cada variável do recurso, adicionar o bloco no arquivo variables.tf
    with open('variable.txt', 'r') as f:
        variable_model = f.read()
    variables_path = f'{path}/variables.tf'
    variables_append = f'#Resource: {resources[resource_id]}{resource_i}\n'
    for var_name, var_value in dic_var.items():
        model_copy = variable_model
        model_copy = model_copy.replace("var_name", f'{var_name}{resource_i}').replace("value", var_value)
        variables_append += model_copy
        variables_append += '\n'
    with open (variables_path, 'a') as f:
        f.write(variables_append)
    #-----

    #Aplicar mudanças na Nuvem
    apply_terraform_changes()


#Função que retorna um dicionário no formato sg_name => sg_id
#Útil para listar sg disponíveis ao criar uma instância, para que o usuário crie um
def list_sg_ids():
    name_id_sg = {}
    state_path = path + '/terraform.tfstate'
    with open(state_path, 'r') as json_file:
        resources = json.load(json_file)["resources"]
    for r_obj in resources:
        if r_obj['type'] == "aws_security_group":
            id = r_obj["instances"][0]["attributes"]["id"]
            name = r_obj["instances"][0]["attributes"]["name"]
            name_id_sg[name]=id
    return name_id_sg


#Deleta todos os arquivos .tf que não sejam o main e o variables
#Deleta todas as variáveis do variables.tf
def delete_files():
    for file in os.listdir(path):
        if re.findall(".tf$", file)!=[]:
            if file !='main.tf' and file!='variables.tf':
                file_path = f'{path}/{file}'
                print(file_path)
                os.remove(file_path)
    
    variables_path = f'{path}/variables.tf'
    with open(variables_path, 'w') as f:
        f.write("")


#Função que deleta um recurso específico
def delete_resource():
    #Mapeia recursos disponíveis, a partir do variables.tf
    variables_path = f'{path}/variables.tf'
    all_resources = []
    with open(variables_path, 'r') as f:
        for line in f.readlines():
            if '#Resource: ' in line:
                all_resources.append(line.split(" ")[1].strip('\n'))
    #------

    #Pergunta ao usuário qual será deletado
    print("Digite o número do recurso a ser removido:")
    for i, r in enumerate(all_resources):
        print(f'{r} => {i}')

    ask_resource = True
    while ask_resource:
        del_resource_id = int(input("-- "))
        if del_resource_id>=0 and del_resource_id<len(all_resources):
            ask_resource = False

    resource_del = all_resources[del_resource_id]
    #------

    #Deleta arquivo .tf do Recurso
    for file in os.listdir(path):
        if re.findall(".tf$", file)!=[]:
            if file !='main.tf' and file!='variables.tf':
                if file == f'{resource_del}.tf':
                    file_path = f'{path}/{file}'
                    print(file_path)
                    os.remove(file_path)
    #------

    #Reescreve variables.tf, copiando tudo menos as variáveis do recurso deletado
    temp_path = f'{path}/temp.txt'
    with open(variables_path, "r") as input_file:
        with open(temp_path, "w") as output_file:
            found = False
            for line in input_file:
                if found == False:
                    if f'#Resource: {resource_del}' in line:
                        found = True
                    else:
                        output_file.write(line)
                else:
                    if '#Resource: ' in line:
                        output_file.write(line)
                        found = False
    #------           

    #Substitui o original pelo temporário, que não possui as variáveis do recurso deletado
    os.replace(f'{path}/temp.txt', f'{path}/variables.tf')

    #Aplicar mudanças na Nuvem
    # apply_terraform_changes()


def apply_terraform_changes():
    command = 'terraform plan -out="tfplan.out"'
    print(command)
    p = Popen(command, cwd=path)
    p.communicate()
    p = Popen('terraform apply "tfplan.out"', cwd=path)
    p.communicate()



p = Popen("terraform init", cwd=path)
p.communicate()

program = True
create = 0
delete_all = 2
list_ = 3
exit = 4
delete = 1
pergunta = '''

Criar => 0
Deletar recurso => 1
Deletar toda a Infraestrutura => 2
Listar Infraestrutura => 3
Sair => 4

Número da Ação: '''

print('\n')
print("Interactive Terraform")
while (program):
    ans = int(input(pergunta))

    if ans == create:
        print('Criar')
        create_resource()

    elif ans==delete_all:
        print('Deletar')
        delete_files()
        p = Popen("terraform destroy -auto-approve", cwd=path)
        p.communicate()

    elif ans==list_:
        sg_dic = list_sg_ids()
        sg_names = list(sg_dic.keys())
        sg_ids = list(sg_dic.values())

        print('Listar')
        state_path = path + '/terraform.tfstate'
        with open(state_path, 'r') as json_file:
            resources = json.load(json_file)["resources"]

        for r in resources:
            type_ = r["type"]
            name = r["name"]
            region = r["instances"][0]["attributes"]["arn"].split(":")[3]
            print(f'Tipo:     {type_}')
            print(f'Nome:     {name}')
            print(f'Região:   {region}')
            if "instance" in name:
                security_group = sg_names[sg_ids.index(r["instances"][0]["attributes"]["vpc_security_group_ids"][0])]
                print(f'Security Groups: {security_group}')

            if "security" in name:
                rules_used = ["cidr_blocks", "from_port", "to_port", "protocol"]
                rules = r["instances"][0]["attributes"]["ingress"][0]
                for n_rule, rule in rules.items():
                    if n_rule in rules_used:
                        print(f'{n_rule.title()}  :  {rule}')
            
            print('\n')

    elif ans==delete:
        print('Deletar recurso')
        delete_resource()

    elif ans==exit:
        program = 0

    else:
        print('Resposta Inválida')




