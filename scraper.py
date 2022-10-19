from ipaddress import v4_int_to_packed
import pandas as pd
from bs4 import BeautifulSoup as bs
import cloudscraper
import time
import numpy as np


def get_links(project_link, max_page_range=50):
    links = []
    scraper = cloudscraper.create_scraper()
    
    for i in range(1, max_page_range+1):
        url = project_link + "/"+ str(i)
        s = scraper.get(url)
        while s.status_code != 200:
            scraper = cloudscraper.create_scraper()
            s = scraper.get(url)
            time.sleep(10)

        print(url, s.status_code)
        project = bs(s.content, 'html.parser')

        # have to add try except in event of no page found
        for j in project.find_all("a", {"class": "nav-link"}):
            link = "https://www.propertyguru.com.sg/"+str(j.get('href'))
            link_list = link.split("#")
            if link_list[0] not in links:
                print(link_list[0])
                links.append(link)

        print(url, s.status_code)
        if i == 5:
            break
        time.sleep(5)
    return links


def get_unit(project_links, type='condo'):
    units = []
    name = []
    project_type = []
    project_link = []


    scraper = cloudscraper.create_scraper()

    for project in project_links:
        s = scraper.get(project)
        print(project, s.status_code)
        while s.status_code != 200:
            scraper = cloudscraper.create_scraper()
            s = scraper.get(project)
            print(project, s.status_code) 
            time.sleep(5)
 
        value = bs(s.content, 'html.parser').find_all('td', {'class': "value-block"})
        project_name = value[0].text
        name.append(project_name)
        project_type.append(type)
        project_link.append(project)
        try:
            project_unit = int(value[-1].text)
            units.append(project_unit)
        except:
            units.append(np.nan)
        time.sleep(5)


    output_df = pd.DataFrame({"project_name": name,
                              "project_links": project_link,
                              "type": project_type,
                              "units": units})

    return output_df


def get_last_page(url):
    scraper = cloudscraper.create_scraper()
    s = scraper.get(url)
    project = bs(s.content, 'html.parser')
    last_page = project.find_all("ul", {"class": "pagination"})[0].find_all("a")[-2].text

    try:
        page = int(last_page)
        return page
    except:
        print("error")
        page = input("please enter target page: ")
        return int(page)


if __name__ == "__main__":
    # condo_url = "https://www.propertyguru.com.sg/condo-directory/search-condo-project"
    # page = get_last_page(condo_url)
    # condo_links = get_links(condo_url, max_page_range= page)  
    # project_condo_links =  pd.DataFrame({'links', condo_links})
    # project_condo_links.to_csv('condo_links.csv', index = False)
    condo_links = pd.read_csv("condo_links.csv")
    condo_project_links = list(condo_links.links)
    condo_units = get_unit(condo_project_links, type='condo')
    condo_units.to_csv("condo_unit.csv", index=False)


    # apartment_url = "https://www.propertyguru.com.sg/condo-directory/search-apartment-project"
    # page = get_last_page(apartment_url)
    # apartment_links = get_links( apartment_url, max_page_range= page)  # to improve on range
    # project_apartment_links =  pd.DataFrame({'links', apartment_links})
    # project_apartment_links.to_csv('apartment_links.csv', index = False)
    # apartment_links = pd.read_csv("apartment_links.csv")
    # apartment_project_links = list(apartment_links.links)
    # apartment_units = get_unit(apartment_project_links, type='apartment')
    # apartment_units.to_csv("apartment_unit.csv", index=False)
