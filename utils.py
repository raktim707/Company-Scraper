def find_nature(psc):
    nature_pcs=psc.findAll("dd")
    for tag in nature_pcs:
        result=tag.get_text(strip=True)
        id=tag.get('id')
        if "Ownership of shares" in result and id.endswith("-percent"):
            psc_nature=result.split('–')[-1].strip()
            break
        else:
            psc_nature=None
    return psc_nature

def name_of_psc(psc_name):
    psc=psc_name.find("span").get_text(strip=True)
    return psc
