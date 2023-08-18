def sort_age ( lst ) :
    list1 = [ ]
    i = 0
    smallest = lst [ 0 ] [ 1 ]
    s = lst [ 0 ]
    for i in range ( 1 , len ( lst ) ) :
        if ( lst [ i ] [ 1 ] < smallest ) :
            smallest = lst [ i ] [ 1 ]
            s = lst [ i ]
    list1 . append ( s )
    return list1

sort_age([("F", 19)])
sort_age([("M", 35), ("F", 18), ("M", 23), ("F", 19), ("M", 30), ("M", 17)])
sort_age([("F", 18), ("M", 23), ("F", 19), ("M", 30), ("M", 17)])
sort_age([("F", 18), ("M", 23), ("F", 19), ("M", 30)])
sort_age([("M", 23), ("F", 19), ("M", 30)])
sort_age([])
