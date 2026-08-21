import os
import sys
import shutil
import subprocess

# Repository root (one level above /scripts), so the script works regardless of cwd.
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


def _abs(*parts):
    return os.path.join(REPO_ROOT, *parts)


def _flatten_java_outputs(output_dir):
    """Move any .java files from nested subdirectories into output_dir, then
    remove the now-empty nesting. Some tools (e.g. IntelliMerge) mirror the
    absolute path of the input under the output directory; this normalises
    the layout for the evaluator."""
    moved_any = False
    for root, _dirs, files in os.walk(output_dir):
        if os.path.abspath(root) == os.path.abspath(output_dir):
            continue
        for file in files:
            if file.endswith(".java"):
                src = os.path.join(root, file)
                dst = os.path.join(output_dir, file)
                if os.path.exists(dst):
                    # Avoid silent overwrite; append the parent dir name.
                    parent = os.path.basename(root)
                    dst = os.path.join(output_dir, f"{parent}__{file}")
                shutil.move(src, dst)
                moved_any = True
    # Remove leftover empty subdirectories.
    for entry in os.listdir(output_dir):
        sub = os.path.join(output_dir, entry)
        if os.path.isdir(sub):
            shutil.rmtree(sub, ignore_errors=True)
    return moved_any


def run_intellimerge():
    jar_path = _abs("merge_tools", "IntelliMerge", "IntelliMerge-1.0.9-all.jar")
    for i in range(1, 40):
        scenario = f"scenario_{i}"
        left = _abs("scenarios_base", "IntelliMerge", scenario, "left")
        base = _abs("scenarios_base", "IntelliMerge", scenario, "base")
        right = _abs("scenarios_base", "IntelliMerge", scenario, "right")
        output = _abs("output", "IntelliMerge", "scenarios", scenario)

        os.makedirs(output, exist_ok=True)

        command = [
            "java", "-jar", jar_path,
            "-d", left, base, right,
            "-o", output,
        ]
        print(f"[IntelliMerge] Executando cenário {i}")
        subprocess.run(command, check=True)

        if _flatten_java_outputs(output):
            print(f"[IntelliMerge] Estrutura aninhada normalizada no cenário {i}")
        print(f"[IntelliMerge] Cenário {i} processado com sucesso")


def run_fstmerge():
    jar_path = _abs("merge_tools", "FSTMerge", "featurehouse_20220107.jar")
    for i in range(1, 40):
        scenario = f"scenario_{i}"
        base_dir = _abs("scenarios_base", "FSTMerge", scenario)
        expression = os.path.join(base_dir, "merge.expression")
        output_dir = _abs("output", "FSTMerge", "scenarios", scenario)
        os.makedirs(output_dir, exist_ok=True)

        command = [
            "java", "-jar", jar_path,
            "--expression", expression,
            "--base-directory", base_dir,
        ]
        print(f"[FSTMerge] Executando cenário {i}")
        subprocess.run(command, check=True)

        merge_output_dir = os.path.join(base_dir, "merge")
        if os.path.exists(merge_output_dir):
            for root, _dirs, files in os.walk(merge_output_dir):
                for file in files:
                    if file.endswith(".java"):
                        src_file = os.path.join(root, file)
                        dst_file = os.path.join(output_dir, file)
                        shutil.move(src_file, dst_file)
                        print(f"[FSTMerge] Arquivo {file} movido para {output_dir}")
            shutil.rmtree(merge_output_dir, ignore_errors=True)

        print(f"[FSTMerge] Cenário {i} processado com sucesso")


def run_jdime():
    jdime_basename = "JDime.bat" if sys.platform == "win32" else "JDime"
    jdime_exec = _abs("merge_tools", "JDime", "jdime", "build", "install", "JDime", "bin", jdime_basename)
    java_home = _abs("java_dependencies", "java-versions", "jdk8u392-b08")

    failed_scenarios = []
    successful_scenarios = []

    for i in range(1, 40):
        scenario = f"scenario_{i}"
        left = _abs("scenarios_base", "JDime", scenario, "left")
        base = _abs("scenarios_base", "JDime", scenario, "base")
        right = _abs("scenarios_base", "JDime", scenario, "right")
        output = _abs("output", "JDime", "scenarios", scenario)
        os.makedirs(output, exist_ok=True)

        command = [
            jdime_exec,
            "-f",
            "--accept-non-java",
            "--mode", "structured",
            "--recursive",
            "--exit-on-error",
            "--output", output,
            left, base, right,
        ]
        env = os.environ.copy()
        env["JAVA_HOME"] = java_home

        print(f"[JDime] Executando cenário {i}")
        try:
            subprocess.run(
                command, env=env, cwd=os.path.dirname(jdime_exec), check=True,
                capture_output=True, text=True,
            )
            successful_scenarios.append(i)
            print(f"[JDime] Cenário {i} executado com sucesso")
        except subprocess.CalledProcessError as e:
            failed_scenarios.append(i)
            print(f"[JDime] Falha no cenário {i}: {e}")
            print(f"[JDime] Erro de saída: {e.stderr}")
            print(f"[JDime] Repetindo em modo estruturado para cenário {i}")
            try:
                alt_command = [
                    jdime_exec, "-f", "--accept-non-java", "--mode", "structured",
                    "--recursive", "--exit-on-error",
                    "--output", output, left, base, right,
                ]
                subprocess.run(
                    alt_command, env=env, cwd=os.path.dirname(jdime_exec), check=True,
                    capture_output=True, text=True,
                )
                print(f"[JDime] Cenário {i} executado em repetição estruturada")
                failed_scenarios.remove(i)
                successful_scenarios.append(i)
            except subprocess.CalledProcessError as alt_e:
                print(f"[JDime] Cenário {i} falhou novamente em modo estruturado: {alt_e}")
        except Exception as e:
            failed_scenarios.append(i)
            print(f"[JDime] Erro inesperado no cenário {i}: {e}")

    print(f"\n[JDime] Resumo da execução:")
    print(f"Cenários executados com sucesso: {len(successful_scenarios)}")
    print(f"Cenários com falha: {len(failed_scenarios)}")
    if failed_scenarios:
        print(f"Cenários que falharam: {failed_scenarios}")
    if successful_scenarios:
        print(f"Cenários executados: {successful_scenarios}")


def main():
    print("Escolha a ferramenta de merge para rodar os 39 cenários:\n")
    print("1 - IntelliMerge")
    print("2 - FSTMerge")
    print("3 - JDime")
    choice = input("\nDigite o número da ferramenta desejada: ").strip()

    try:
        if choice == '1':
            run_intellimerge()
        elif choice == '2':
            run_fstmerge()
        elif choice == '3':
            run_jdime()
        else:
            print("Opção inválida.")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar o cenário: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")


if __name__ == "__main__":
    main()
