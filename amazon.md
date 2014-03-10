# Goal
Create a command line application called amazon.py.  The application accepts a couple of flags and an user query, and then prints out the first page of amazon store results based on the user supplied information.

## Example

    ./amazon.py --sort rating --desc office chairs

            Flash Furniture Mid-Back Black Mesh Computer Chair
                Price: $59.88
                    Rating: ★★★☆☆ (242 reviews)
                        Url: http://www.amazon.com/Flash-Furniture-Mid-Back-Black-Computer

                                Boss Black LeatherPlus Executive Chair
                                    Price: $159.99
                                        Rating: ★★★★☆ (502 reviews)
                                            Url: http://www.amazon.com/Flash-Furniture-Mid-Back-Black-Computer

                                                ... and so on ...

## Requirements/guidelines

1.  The program must scrape the HTML of the following page: (don't use an Amazon API)
    http://www.amazon.com/s/?field-keywords=query
    2.  The program can use any python library(s).
    3.  The program must allow the user to specify a search query.
    4.  The program must accept the options `--sort {rating, price, name}` and `--{asc, desc}` at a minimum.
    5.  Bonus points for additional flags such as `--prime` (only select items which have amazon prime benefits)
    6.  The program should return no more than 10 results.  Bonus points if you allow `--limit {number of results}`.

## Judging criteria

1. Meets or exceeds all of the above requirements
2. No errors, clean output (ie. don't leave debugging stuff in the code)
3. Code is clean and simple to read and execute
