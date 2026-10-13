import numpy as np
START = 'CRYST1    0.000    0.000    0.000  90.00  90.00  90.00 P 1           1'
END = 'END'
# x_step1 = 1.418, x_step2 = 2.836, y_step = 1.229
def find_parameter(targetfile):
    xmin = 100
    ymin = 100
    zmin = 100
    xmax = -120
    ymax = -120
    zmax = -120
    with open(targetfile,'r') as file:
        while True:
            line = file.readline()
            line = line.split()
            if len(line) > 1:
                if line[0] == 'ATOM' and line[4] == 'X' and line[2] == 'C':
                    line[6] = round(float(line[6]), 3)
                    line[7] = round(float(line[7]), 3)
                    line[8] = round(float(line[8]), 3)
                    if line[6] <= xmin:
                        xmin = line[6]
                    if line[7] <= ymin:
                        ymin = line[7]
                    if line[8] <= zmin:
                        zmin = line[8]
                    if line[6] >= xmax:
                        xmax = line[6]
                    if line[7] >= ymax:
                        ymax = line[7]
                    if line[8] >= zmax:
                        zmax = line[8]
                elif line[0] == 'ATOM' and line[4] != 'X' and line[2] == 'O12':
                    line[5] = round(float(line[5]), 3)
                    line[6] = round(float(line[6]), 3)
                    line[7] = round(float(line[7]), 3)
                    if line[5] <= xmin:
                        xmin = line[5]
                    if line[6] <= ymin:
                        ymin = line[6]
                    if line[7] <= zmin:
                        zmin = line[7]
                    if line[5] >= xmax:
                        xmax = line[5]
                    if line[6] >= ymax:
                        ymax = line[6]
                    if line[7] >= zmax:
                        zmax = line[7]
            elif line[0] == 'END' or line[0] == 'ENDMDL':
                break
            y_step = 1.229
            xmin_step = 1.418
            xmax_step = 2.836
    y_num = int((ymax-ymin)/y_step+1) + 1
    return [xmin,xmin+0.709,xmin_step,xmax_step,ymax,y_step,y_num,xmax]

def pore(targetfile,output,matrix,parameter):
    xmin = parameter[0]
    xmin1 = parameter[1]
    xmin_step = parameter[2]
    xmax_step = parameter[3]
    x_step = xmin_step + xmax_step
    y_max = parameter[4]
    y_step = parameter[5]
    x_max = parameter[7]
    output = open(output, 'w')
    output.write(START + '\n')
    with open(targetfile, 'r') as file:
        restore = []
        while True:
            line = file.readline()
            line = line.split()
            i = 0
            j = 0
            if len(line)>1 and line[0] == 'ATOM':
                if line[2] == 'C':
                    line[6] = float(line[6])
                    line[7] = float(line[7])
                    line[8] = float(line[8])
                    if abs(int((y_max-line[7])/y_step) - (y_max-line[7])/y_step) > abs(int((y_max-line[7])/y_step + 1) - (y_max-line[7])/y_step):
                        i = int((y_max-line[7])/y_step+1)
                    elif abs(int((y_max - line[7]) / y_step) - (y_max - line[7]) / y_step) < abs(int((y_max - line[7]) / y_step + 1) - (y_max - line[7]) / y_step):
                        i = int((y_max - line[7]) / y_step)
                    if i % 2 == 0:
                        # 先要判断该点属于哪里
                        if abs((line[6]-xmin)/x_step) < abs((line[6]-xmin-xmax_step)/x_step):
                            # 再尝试把j得出
                            if abs(int((line[6]-xmin) / x_step) - (line[6]-xmin) / x_step) > abs(int((line[6]-xmin) / x_step+1) - (line[6]-xmin) / x_step):
                                j = int((line[6]-xmin) / x_step + 1)
                                if j != 0:
                                    j = 1+2j
                                    if j >= 29:
                                        j = 29
                            else:
                                j = int((line[6]-xmin) / x_step)
                                if j != 0:
                                    j = 1+2j
                                    if j >= 29:
                                        j = 29
                        else:
                            if abs(int((line[6]-xmin-xmax_step) / x_step) - (line[6]-xmin-xmax_step) / x_step) > abs(int((line[6]-xmin-xmax_step) / x_step + 1) - (line[6]-xmin-xmax_step) / x_step):
                                j = int((line[6]-xmin-xmax_step) / x_step + 1)
                                if j != 0:
                                    j = 2 * j
                                    if j >= 28:
                                        j = 28
                            else:
                                j = int((line[6]-xmin-xmax_step) / x_step)
                                if j != 0:
                                    j = 2 * j
                                    if j >= 28:
                                        j=28
                    else:
                        if abs((line[6] - xmin1) / x_step) < abs((line[6] - xmin1 - xmin_step) / x_step):
                            # 再尝试把j得出
                            if abs(int((line[6] - xmin1) / x_step) - (line[6] - xmin1) / x_step) > abs(int((line[6] - xmin1) / x_step + 1) - (line[6] - xmin1) / x_step):
                                j = int((line[6] - xmin1) / x_step + 1)
                                j = j * 2
                                if j >= 28:
                                    j = 28
                            else:
                                j = int((line[6] - xmin1) / x_step)
                                j = j * 2
                                if j >= 28:
                                    j = 28
                        else:
                            if abs(int((line[6] - xmin1 - xmin_step) / x_step) - (line[6] - xmin1 - xmin_step) / x_step) > abs(int((line[6] - xmin1 - xmin_step) / x_step + 1) - (line[6] - xmin1 - xmin_step) / x_step):
                                j = int((line[6] - xmin1 - xmin_step) / x_step + 1)
                                if j != 0:
                                    j = 1+j*2
                                    if j >= 29:
                                        j = 29
                            else:
                                j = int((line[6] - xmin1 - xmin_step) / x_step)
                                if j != 0:
                                    j = 1+j*2
                                    if j >= 29:
                                        j = 29
                    if matrix[i][j] == 1:
                        print('this is pore')
                    elif matrix[i][j] == 0:
                        restore.append(line)
            elif line[0] == 'END':
                break
    for i in restore:
        output.write('%4s%7s%5s%4s%2s%4s%12.3f%8.3f%8.3f%6s%6s\n' % (i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8], i[9], i[10]))
    output.write(END)
    output.close()

# 不考虑边缘太过复杂，很难处理
def pore_matrix(row,column,delete_num,state): #column可以默认毕竟不变
    matrix = np.zeros((row, column))
    # 寻找矩阵的中心，即matrix[row/2][column/2]
    # 不考虑边缘开孔有两种情况，删对位C加两个六边形的孔面积，删邻位C加一个六边形的孔面积
    matrix[int(row/2)][int(column/2)-1] = 1
    matrix[int(row/2)][int(column/2)] = 1
    if delete_num%2 == 0:
        if state == 1: # state = 1代表边缘带有C原子, state = 0代表边缘光滑
            delete_num = delete_num/2
            i_top = int((delete_num-1)/2)
            i_bottom = int(delete_num/2)
            for i in range(1,i_bottom+1):
                # matrix[int(row/2)-i][int(column/2)] = 1
                # matrix[int(row/2)-i][int(column/2)-1] = 1
                matrix[int(row / 2) - i][int(column / 2)-1] = 1
                matrix[int(row / 2) - i][int(column / 2)] = 1
            for i in range(1,i_top+1):
                matrix[int(row/2)+i][int(column/2)-1] = 1
                matrix[int(row/2)+i][int(column/2)] = 1
        elif state == 0:
            delete_num = delete_num/2
            i_top = int((delete_num-1)/2)
            i_bottom = int(delete_num/2)
            for i in range(1,i_bottom+1):
                if i%2 == 0:
                    matrix[int(row/2)-i][int(column/2)] = 1
                    matrix[int(row/2)-i][int(column/2)-1] = 1
                else:
                    matrix[int(row/2)-i][int(column/2)-1] = 1
                    matrix[int(row/2)-i][int(column/2)-2] = 1
            for i in range(1,i_top+1):
                if i%2 == 0:
                    matrix[int(row/2)+i][int(column/2)] = 1
                    matrix[int(row/2)+i][int(column/2)-1] = 1
                else:
                    matrix[int(row/2)+i][int(column/2)-1] = 1
                    matrix[int(row/2)+i][int(column/2)-2] = 1
    else:
        i_all = int((delete_num-1)/2)
        if state == 1:
            for i in range(1,i_all+1):
                matrix[int(row/2)-i][int(column/2)] = 1
                matrix[int(row/2)-i][int(column/2)-1] = 1
                matrix[int(row/2)+i][int(column/2)-1] = 1
                matrix[int(row/2)+i][int(column/2)] = 1
            # matrix[int(row/2)-i_all][int(column/2)-2] = 1
        elif state == 0:
            for i in range(1,i_all+1):
                if i%2 == 0:
                    # matrix[int(row/2)-i][int(column/2)] = 1
                    # matrix[int(row/2)-i][int(column/2)-1] = 1
                    # matrix[int(row/2)+i][int(column/2)-1] = 1
                    # matrix[int(row/2)+i][int(column/2)] = 1
                    matrix[int(row/2)-i][int(column/2)-2] = 1
                    matrix[int(row/2)-i][int(column/2)-1] = 1
                    matrix[int(row/2)+i][int(column/2)-1] = 1
                    matrix[int(row/2)+i][int(column/2)-2] = 1
                else:
                    matrix[int(row/2)-i][int(column/2)-2] = 1
                    matrix[int(row/2)-i][int(column/2)-1] = 1
                    matrix[int(row/2)+i][int(column/2)-1] = 1
                    matrix[int(row/2)+i][int(column/2)-2] = 1
            # matrix[int(row/2)-i_all][int(column/2)-2] = 1
    return matrix

# 存在问题1就删两个
parameter = find_parameter(r'C:\Users\Admin\Desktop\工作\GRA论文\挖孔graphe\pore22.pdb')
matrix = pore_matrix(parameter[6],30,delete_num=1,state=0)
# matrix = np.zeros((parameter[6], 30))
# matrix[0][2] = 1
pore(r'C:\Users\Admin\Desktop\工作\GRA论文\挖孔graphe\pore22.pdb',r'C:\Users\Admin\Desktop\工作\GRA论文\挖孔graphe\pore2.pdb',matrix,parameter)
print(matrix)
