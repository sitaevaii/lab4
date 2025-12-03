import diagrams

def reports():
    while True:
        print("\n" + "=" * 50)
        print("АНАЛИТИЧЕСКИЕ ОТЧЕТЫ ПО ПРОЕКТУ HDFS")
        print("=" * 50)
        print("1. Гистограмма времени нахождения задач в открытом состоянии")
        print("2. Гистограмма времени распределения задач по состояниям")
        print("3. График количества заведенных и закрытых задач в день")
        print("4. График активности пользователей (исполнитель + репортер)")
        print("5. График количества задач по степени серьезности")
        print("0. ВЫХОД")
        print("=" * 50)
        choice = input("\nВыберите номер отчета (0-5): ").strip()

        if choice == "0":
            print("Выход из программы...")
            break

        elif choice == "1":
            diagrams.hist1()

        elif choice == "2":
            diagrams.diag2()

        elif choice == "3":
            diagrams.graf3()

        elif choice == "4":
            diagrams.graf4()

        elif choice == "5":
            diagrams.graf6()

        else:
            print("Ошибка: выберите число от 0 до 5")
        if choice != "0":
            input("\nНажмите Enter чтобы вернуться в меню...")