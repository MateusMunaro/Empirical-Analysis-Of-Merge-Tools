import subprocess
import os
import shutil

def run_intellimerge():
    jar_path = "./merge_tools/IntelliMerge/IntelliMerge-1.0.9-all.jar"
    for i in range(1, 40):
        scenario = f"scenario_{i}"
        left = f"./scenarios_base/IntelliMerge/{scenario}/left"
        base = f"./scenarios_base/IntelliMerge/{scenario}/base"
        right = f"./scenarios_base/IntelliMerge/{scenario}/right"
        output = f"./output/IntelliMerge/scenarios/{scenario}"

        # Garantir que o diretório de saída existe
        os.makedirs(output, exist_ok=True)

        command = [
            "java", "-jar", jar_path,
            "-d", left, base, right,
            "-o", output
        ]
        print(f"[IntelliMerge] Executando cenário {i}")
        subprocess.run(command, check=True)
        
        # Corrigir a estrutura de pastas criada pelo IntelliMerge
        nested_path = f"{output}/workspaces/Pesquisa-cientifica"
        if os.path.exists(nested_path):
            # Encontrar todos os arquivos .java na pasta aninhada
            for root, dirs, files in os.walk(nested_path):
                for file in files:
                    if file.endswith('.java'):
                        src_file = os.path.join(root, file)
                        dst_file = os.path.join(output, file)
                        shutil.move(src_file, dst_file)
                        print(f"[IntelliMerge] Arquivo {file} movido para {output}")
            
            # Remover a estrutura de pastas desnecessária
            shutil.rmtree(f"{output}/workspaces")
            print(f"[IntelliMerge] Estrutura de pastas desnecessária removida do cenário {i}")
        
        print(f"[IntelliMerge] Cenário {i} processado com sucesso")
        
def run_fstmerge():
    jar_path = "./merge_tools/FSTMerge/featurehouse_20220107.jar"
    for i in range(1, 40):
        scenario = f"scenario_{i}"
        base_dir = f"./scenarios_base/FSTMerge/{scenario}"
        expression = f"{base_dir}/merge.expression"

        output_dir = f"./output/FSTMerge/scenarios/{scenario}"
        os.makedirs(output_dir, exist_ok=True)

        command = [
            "java", "-jar", jar_path,
            "--expression", expression,
            "--base-directory", base_dir, 
        ]
        print(f"[FSTMerge] Executando cenário {i}")
        subprocess.run(command, check=True)
        
        # Mover o arquivo do diretório de merge para o diretório de saída correto
        merge_output_dir = f"{base_dir}/merge"
        if os.path.exists(merge_output_dir):
            # Encontrar todos os arquivos .java na pasta merge
            for root, dirs, files in os.walk(merge_output_dir):
                for file in files:
                    if file.endswith('.java'):
                        src_file = os.path.join(root, file)
                        dst_file = os.path.join(output_dir, file)
                        shutil.move(src_file, dst_file)
                        print(f"[FSTMerge] Arquivo {file} movido para {output_dir}")
            
            # Remover a pasta merge se estiver vazia
            try:
                if not os.listdir(merge_output_dir):
                    os.rmdir(merge_output_dir)
                    print(f"[FSTMerge] Pasta merge removida do cenário {i}")
            except OSError:
                print(f"[FSTMerge] Pasta merge não pôde ser removida (pode conter outros arquivos)")
        
        print(f"[FSTMerge] Cenário {i} processado com sucesso")

def run_jdime():
    jdime_exec = "./merge_tools/JDime/jdime/build/install/JDime/bin/JDime"
    java_home = "/workspaces/Pesquisa-cientifica/java_dependencies/java-versions/jdk8u392-b08"
    
    failed_scenarios = []
    successful_scenarios = []

    for i in range(1, 40):
        scenario = f"scenario_{i}"
        left = f"./scenarios_base/JDime/{scenario}/left"
        base = f"./scenarios_base/JDime/{scenario}/base"
        right = f"./scenarios_base/JDime/{scenario}/right"
        output = f"./output/JDime/scenarios/{scenario}"

        # Ensure output directory exists
        os.makedirs(output, exist_ok=True)

        command = [
            jdime_exec,
            "-f",
            "--mode", "structured",
            "--output", output,
            left, base, right
        ]
        env = os.environ.copy()
        env["JAVA_HOME"] = java_home

        print(f"[JDime] Executando cenário {i}")
        
        try:
            result = subprocess.run(command, env=env, check=True, 
                                  capture_output=True, text=True)
            successful_scenarios.append(i)
            print(f"[JDime] Cenário {i} executado com sucesso")
            
        except subprocess.CalledProcessError as e:
            failed_scenarios.append(i)
            print(f"[JDime] Falha no cenário {i}: {e}")
            print(f"[JDime] Erro de saída: {e.stderr}")
            
            # Try alternative merge mode for failed scenarios
            print(f"[JDime] Tentando modo alternativo para cenário {i}")
            try:
                alt_command = [
                    jdime_exec,
                    "-f",
                    "--mode", "unstructured",  # Try unstructured mode
                    "--output", output,
                    left, base, right
                ]
                subprocess.run(alt_command, env=env, check=True, 
                             capture_output=True, text=True)
                print(f"[JDime] Cenário {i} executado com sucesso em modo não estruturado")
                failed_scenarios.remove(i)
                successful_scenarios.append(i)
                
            except subprocess.CalledProcessError as alt_e:
                print(f"[JDime] Cenário {i} falhou também em modo não estruturado: {alt_e}")
                
        except Exception as e:
            failed_scenarios.append(i)
            print(f"[JDime] Erro inesperado no cenário {i}: {e}")
    
    # Summary report
    print(f"\n[JDime] Resumo da execução:")
    print(f"Cenários executados com sucesso: {len(successful_scenarios)}")
    print(f"Cenários com falha: {len(failed_scenarios)}")
    
    if failed_scenarios:
        print(f"Cenários que falharam: {failed_scenarios}")
    
    if successful_scenarios:
        print(f"Cenários executados: {successful_scenarios}")


def run_automerge():
    # Configurar caminhos base
    workspace = "/workspaces/Pesquisa-cientifica"
    java_exec = f"{workspace}/java_dependencies/java-versions/jdk-11.0.2/bin/java"
    
    # Caminhos para JARs e bibliotecas
    automerge_jar = f"{workspace}/merge_tools/AutoMerge/AutoMerge.jar"
    activation_jar = f"{workspace}/libs/activation-1.1.1.jar"
    
    # Diretório para bibliotecas do JavaFX
    javafx_dir = f"{workspace}/libs/javafx-sdk"
    os.makedirs(javafx_dir, exist_ok=True)
    
    # Baixar e extrair JavaFX SDK se necessário
    javafx_jars = []
    if not os.path.exists(f"{javafx_dir}/lib"):
        print("Baixando e extraindo JavaFX SDK...")
        javafx_url = "https://download2.gluonhq.com/openjfx/11.0.2/openjfx-11.0.2_linux-x64_bin-sdk.zip"
        try:
            # Baixar o arquivo zip
            zip_path = f"{workspace}/libs/javafx.zip"
            subprocess.run(["wget", "-O", zip_path, javafx_url], check=True)
            
            # Extrair o arquivo
            subprocess.run(["unzip", "-q", zip_path, "-d", f"{workspace}/libs"], check=True)
            
            # Mover os arquivos para o diretório correto
            subprocess.run(["mv", f"{workspace}/libs/javafx-sdk-11.0.2", javafx_dir], check=True)
            
            # Limpar o arquivo zip
            if os.path.exists(zip_path):
                os.remove(zip_path)
                
        except subprocess.CalledProcessError as e:
            print(f"Erro ao baixar/extrair JavaFX: {e}")
            return
    
    javafx_jars = []
    javafx_lib_dir = f"{javafx_dir}/lib"
    if os.path.exists(javafx_lib_dir):
        for jar_file in os.listdir(javafx_lib_dir):
            if jar_file.endswith(".jar"):
                javafx_jars.append(os.path.join(javafx_lib_dir, jar_file))
    
    classpath_components = [automerge_jar, activation_jar] + javafx_jars
    classpath = ":".join(classpath_components)
    
    javafx_modules = "--module-path=" + javafx_lib_dir + " --add-modules=javafx.base,javafx.controls,javafx.graphics"
    
    env = os.environ.copy()
    env["LD_LIBRARY_PATH"] = f"{workspace}/java_dependencies/java-versions/libgit2/build:{env.get('LD_LIBRARY_PATH', '')}"
    
    # Verificar se os diretórios necessários existem
    os.makedirs(f"{workspace}/output/AutoMerge", exist_ok=True)
    
    # Executar para cada cenário
    for i in range(1, 35):
        scenario = f"scenario_{i}"
        
        # Definir caminhos para arquivos
        output_file = f"{workspace}/output/AutoMerge/{scenario}.java"
        
        # Obter diretórios para entrada
        base_dir = f"{workspace}/scenarios_base/AutoMerge/{scenario}/base"
        left_dir = f"{workspace}/scenarios_base/AutoMerge/{scenario}/left"
        right_dir = f"{workspace}/scenarios_base/AutoMerge/{scenario}/right"
        
        # Verificar se os diretórios existem
        if not all(os.path.exists(d) for d in [base_dir, left_dir, right_dir]):
            print(f"[AutoMerge] Pulando cenário {i} - diretórios de entrada não encontrados")
            continue
        
        print(f"[AutoMerge] Executando cenário {i}")
        
        try:
            # Construir o comando com JavaFX
            command = [
                java_exec,
                javafx_modules,
                "-cp", 
                classpath,
                "de.fosd.jdime.Main",
                "-o", 
                f"{workspace}/output/AutoMerge",  # Diretório de saída 
                "-m", 
                "structured",
                "-log", 
                "info",
                "-f",
                "-S",  # Indica que estamos fornecendo diretórios, não arquivos individuais
                left_dir, 
                base_dir, 
                right_dir
            ]
            
            print(f"Executando: {' '.join(command)}")
            
            # Executar o comando
            subprocess.run(command, env=env, check=True)
            
            # Verificar se o arquivo Person.java foi gerado e renomeá-lo se necessário
            person_output = f"{workspace}/output/AutoMerge/Person.java"
            if os.path.exists(person_output):
                shutil.move(person_output, output_file)
                print(f"[AutoMerge] Arquivo renomeado para {scenario}.java")
            
            print(f"[AutoMerge] Cenário {i} concluído com sucesso")
            
        except subprocess.CalledProcessError as e:
            print(f"[AutoMerge] Falha ao executar cenário {i}: {e}")
            
            # Registrar que houve falha para este cenário
            print(f"[AutoMerge] Não foi possível processar o cenário {i}")
        
        print("-------------------------------------------")
    
    print("[AutoMerge] Processamento de todos os cenários concluído")


# MENU INTERATIVO
def main():
    print("Escolha a ferramenta de merge para rodar os 34 cenários:\n")
    print("1 - IntelliMerge")
    print("2 - FSTMerge")
    print("3 - JDime")
    print("4 - AutoMerge")
    choice = input("\nDigite o número da ferramenta desejada: ")

    try:
        if choice == '1':
            run_intellimerge()
        elif choice == '2':
            run_fstmerge()
        elif choice == '3':
            run_jdime()
        elif choice == '4':
            run_automerge()
        else:
            print("Opção inválida.")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar o cenário: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")


if __name__ == "__main__":
    main()
