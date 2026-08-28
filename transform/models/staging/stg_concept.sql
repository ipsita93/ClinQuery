select * from read_csv_auto('{{ var("raw_dir") }}/concept.csv', header=true)
