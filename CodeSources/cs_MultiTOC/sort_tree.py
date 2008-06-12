## Parameters=list: tree, sort_on

tree_list = []
for obj in tree:
    if sort_on == 'date':
        sort_prop = obj[1].get_modification_datetime()
    elif sort_on == 'creation':
        sort_prop = obj[1].get_creation_datetime()
    else:
        sort_prop = obj[1].get_title_editable()
    tree_list.append((sort_prop, obj))
tree_list.sort()
return [obj for (sort_prop, obj) in tree_list]
