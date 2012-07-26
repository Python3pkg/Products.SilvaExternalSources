## Script (Python) "toc_sort_on"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=sort_on,sort_order
##title=
##
#convert the sort_on and sort_order cs params
# to the sort_order key the tocrenderingadapter
# accepts
if sort_order == "reverse":
    if sort_on == "silva":
        return "reversesilva"
    if sort_on == "alpha":
        return "reversealpha"
    elif sort_on == "chronmod":
        return "rchronmod"
return sort_on
