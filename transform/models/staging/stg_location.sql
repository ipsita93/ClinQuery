select * from read_csv_auto('{{ var("raw_dir") }}/location.csv', header=true)
