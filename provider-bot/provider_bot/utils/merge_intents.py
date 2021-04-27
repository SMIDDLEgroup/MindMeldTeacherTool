with open('../domains/internet/specify_day_and_hour/train.txt', 'w') as result_file:
    with open('../domains/internet/specify_day/train.txt') as src1:
            for l1 in src1.readlines():
                with open('../domains/internet/specify_hour/train.txt') as src2:
                    for l2 in src2.readlines():
                        result_file.write(l1.strip() + " " + l2.strip() + '\n')
                        #result_file.write(l1.strip() + " а також " + l2)