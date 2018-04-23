# -*- coding: utf-8 -*-
import xlwt
import os
import xlsxwriter as wx


def writer(filename, titles, items):
        workbook = wx.Workbook(filename)
        top = workbook.add_format(
            {'border': 1, 'align': 'center', 'bg_color': 'white', 'font_size': 11, 'font_name': '微软雅黑'})
        red = workbook.add_format(
            {'font_color': 'white', 'border': 1, 'align': 'center', 'bg_color': '800000', 'font_size': 11,
             'font_name': '微软雅黑', 'bold': True})
        formater = top
        formater.set_align('vcenter')  # 设置单元格垂直对齐
        worksheet = workbook.add_worksheet()  # 创建一个工作表对象
        worksheet.set_default_row(140)

        print(titles)
        for i in range(0, len(titles)):
            worksheet.set_column(0, i, 9.5)  # 设定列的宽度为22像素
            formater = red
            worksheet.write(0, i, titles[i], formater)

        formater = top
        for i in range(0, len(items)):
            for j in range(0, len(items[i])):
                worksheet.set_column(i + 1, j, 40)
                worksheet.write(i + 1, j, items[i][j], formater)
        workbook.close()

