def read_template():
    print(os.curdir)

    with open("latex/template.tex", encoding="utf-8") as template:
        text = template.read()

    splitpos = text.find("%--------------")

    splitpos2 = text.find("%--------------", splitpos + 1)

    templateheader = text[:splitpos]

    template = text[splitpos:splitpos2]

    templatefooter = text[splitpos2:]

    return templateheader, template, templatefooter


def empty_template(kl2kv, teachers, template, year):
    ask_short_text = r"\INes"

    ask_long_text = r"\INe"

    ask_teacher = r"\Choice{" + ",\n".join(f"{name} ({kz})"

                                           for kz, name in sorted(teachers.items())) + "}"

    ask_class = r"\Choice{" + ",".join(klasse + " -- " + kz2full(kl2kv[klasse])

                                       for klasse in kl2kv.keys()

                                       ) + "}"

    args = {

        "year": f"{year - 1}/{year % 100}",

        "abt": ask_short_text,

        "schuelername": ask_long_text,

        "klasse": ask_short_text,

        "kv": ask_class,

        "gegenstand": ask_short_text,

        "prf1": ask_teacher,

        "prf2": ask_teacher,

        "delm": "",

        "dels": "",

        "zeitS": ask_short_text,

        "zeitM": ask_short_text,

        "datum": ask_short_text,

        "raumS": "",

        "raumM": ""

    }

    return myformat(template, args)


def my_call(num, cmd):
    print(f"  start {cmd}  ({num})")

    call(cmd, stdin=DEVNULL, stdout=DEVNULL, shell=True,

         stderr=DEVNULL)

    print(f"  finished {cmd} ({num})")

    with  multiprocessing.Pool(multiprocessing.cpu_count() // 2 - 1) as pool:

        try:

            print("files = ", len(all_files))

            for num, (tex_file, txt) in enumerate(sorted(all_files.items()), 1):

                print(f"create  {num}/{len(all_files)} = {tex_file}")

                with open(tex_file + ".tex", "w", encoding="utf-8") as f:

                    print(templateheader, file=f)

                    print(txt, file=f)

                    if showtermine and tex_file in terminliste:

                        print(TERMINESTART, file=f)

                        for data in terminliste[tex_file]:
                            print(" & ".join(data) + r"\\ \hline", file=f)

                        print(TERMINEEND, file=f)

                    print(templatefooter, file=f)

                pool.apply_async(my_call, args=(f"{num}/{len(all_files)}", f"""latexmk -pdf "{tex_file}" """,))

            pool.close()

            pool.join()

            print("zip")

            call("zip -9 whp.zip *.ics *.pdf", shell=True, stdout=DEVNULL, stderr=DEVNULL)

            call("7z a -mx=9 whp.7z *.ics *.pdf", shell=True, stdout=DEVNULL, stderr=DEVNULL)

        except KeyboardInterrupt as e:

            pass

        finally:

            pool.terminate()

            pool.join()

            print("clean")

            call("latexmk -c", shell=True, stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
