class Pagination:

    def __init__(self, request, data_length, per_num=10, max_show=11):

        try:
            page = int(request.GET.get('page', 1))
            if page <= 0:
                page = 1

        except Exception:
            page = 1

        # per_num = 10
        qd = request.GET.copy()
        total_num, more = divmod(data_length, per_num)  # 整除的数和余数
        if more:
            total_num += 1
        print(total_num)

        # max_show = 11
        half_show = max_show // 2
        if total_num <= max_show:
            page_start = 1
            page_end = total_num
        else:
            if page - half_show <= 0:
                page_start = 1
                page_end = max_show
            elif page + half_show >= total_num:
                page_start = total_num - max_show + 1
                page_end = total_num
            else:
                page_start = page - half_show
                page_end = page + half_show

        page_list = ['<nav aria-label="Page navigation"><ul class="pagination">']
        if page == 1:

            page_list.append('<li class="disabled"><a><span aria-hidden="true">&laquo;</span></a></li>')
        else:
            qd['page'] = page-1
            page_list.append('<li><a href="?{}"><span aria-hidden="true">&laquo;</span></a></li>'.format(qd.urlencode()))

        for i in range(page_start, page_end + 1):
            qd['page'] = i
            if i == page:
                page_list.append('<li class="active"><a href="?{}">{}</a></li>'.format(qd.urlencode(), i))
            else:
                page_list.append('<li><a href="?{}">{}</a></li>'.format(qd.urlencode(), i))
        if page == total_num:
            page_list.append('<li class="disabled"><a><span aria-hidden="true">&raquo;</span></a></li>')
        else:
            qd['page'] = page+1
            page_list.append('<li><a href="?{}"><span aria-hidden="true">&raquo;</span></a></li>'.format(qd.urlencode()))
        page_list.append('</ul></nav>')
        self.page_html = ''.join(page_list)  # 属性
        self.start = (page - 1) * per_num
        self.end = page * per_num
