from bs4 import BeautifulSoup

with open('index.htm','r') as f:
    html_content = f.read()

soup = BeautifulSoup(html_content,'lxml')

tables = soup.find_all('table',{'width':'70%'})

rows:list = tables[0].find_all('tr')
rows.pop(0)

for row in rows:
    if
    x = row.find_all('td',{'class':'CellLeft'})
    print(x,'\n')

# table_regex = r'(<table\s+[^>]*width\s*=\s*"80%".*?</table>)'
# matches = re.findall(table_regex, html_content, re.DOTALL)

# x = etree.fromstring(''.join(matches))
# print(x)

# for match in matches:
#     print(match)