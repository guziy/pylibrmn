infile=test_G_grid.rpn  # RPN input file with one record and tictac's (if needed for the grid type)
outfile=./G_grid_LOLA.rpn # RPN output file (including path or at least './')

# Create field with constant value 180 / PI = 57.29578
r.diag xlin   $infile tmp  -a 0 -b 57.29578

r.diag ggtrig tmp    tmp2 -kind IDF -lon  # ==> outfile=longitude*infile
r.diag newnam tmp2   lon  -name LO
r.diag ggtrig tmp    tmp2 -kind IDF       # ==> outfile=latitude*infile
r.diag newnam tmp2   lat  -name LA

r.diag joinup $outfile lon lat

rm -f tmp tmp2
