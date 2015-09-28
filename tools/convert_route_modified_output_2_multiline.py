#!/usr/local/anaconda/bin/python

input = '/raid2/ymao/VIC_RBM_east_RIPS/VIC_RBM_code_test/output/route_modified/Salmon.DA_heat.UH_1.orig'
output = '/raid2/ymao/VIC_RBM_east_RIPS/VIC_RBM_code_test/output/route_modified/Salmon.DA_heat.UH_1.multi_lines'

f = open(input, 'r')
line = f.readline().rstrip("\n")
f.close()
line_split = line.split()

f = open(output, 'w')
for i in range(len(line_split)/8):
    f.write('{} {} {} {} {} {} {} {}\n'\
        .format(line_split[i*8], line_split[i*8+1], line_split[i*8+2], line_split[i*8+3], \
                line_split[i*8+4], line_split[i*8+5], line_split[i*8+6], line_split[i*8+7]))

f.close()

