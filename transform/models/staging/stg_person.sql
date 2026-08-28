select *
from read_csv_auto('{{ var("raw_dir") }}/person.csv', header=true)
