py-msv - A MetaCSV parser for Python

Copyright (C) 2020 J. Férard <https://github.com/jferard>

License: GPLv3

# Overview
py-mcsv is a [MetaCSV](https://github.com/jferard/MetaCSV) parser for Python. 
I quote the README:

> MetaCSV is an open specification for a CSV file description. This description
> is written in a small auxiliary CSV file that may be stored along wih the 
>CSV file itself. This auxilary file should provide the informations necessary 
>to read and type the content of the CSV file. The standard extension is 
>".mcsv".

py-mcsv is able to read **and type** the rows of a CSV file, provided that you 
have an appropriate MetaCSV file.

(The [ColumnDet](https://github.com/jferard/ColumnDet) package is able to 
generate automatically a sensible MetaCSV file for a given CSV file.)  

# Example
Here's a basic example. The `example.csv` file reads: 

    name,date,count
    foo,2020-11-21,15
    foo,2020-11-22,-8

The `example.mcsv` file reads (see the [MetaCSV format specification](https://github.com/jferard/MetaCSV#full-specification-draft-0):

    domain,key,value
    data,col/1/type,date/YYYY-MM-dd
    data,col/2/type,integer

The code is:

    reader = open_dict_csv("example.csv")
    for row in reader:
        print(row)
        
Output:

    {'count': 15, 'date': datetime.date(2020, 11, 21), 'name': 'foo'}
    {'count': -8, 'date': datetime.date(2020, 11, 22), 'name': 'foo'}

# Usage

The basic usage is:

    reader = open_dict_csv("my-csv-file.csv")
    for row in reader:
        # row is a mapping: field name -> typed value
        ...

This assumes that the MetaCSV file has the same name as the CSV file, with the 
extension ".mcsv". Here, you need the "my-csv-file.mcsv". 

You can provide a path to the MetaCSV file if necessary:

    reader = open_dict_csv("my-csv-file.csv", "my-meta-csv-file.mcsv")
    for row in reader:
        # row is a mapping: field name -> typed value
        ...

If you need the MetaCSV types, just write: 

    reader = open_dict_csv("my-csv-file.csv", skip_types=False)
    for row in reader:
        # the first row is a mapping: field name -> MetaCSV description of type
        # the remaining rows are a mappings: field name -> typed value
        ...

You may wish to access rows as lists:
 
    reader = open_csv("my-csv-file.csv")
    for row in reader:
        # the first row is a header
        # the remaining rows are list of typed values
        ...
