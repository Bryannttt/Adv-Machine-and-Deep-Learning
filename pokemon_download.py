import os
import concurrent.futures
from GoogleImageScraper import GoogleImageScraper
from patch import webdriver_executable

import pandas as pd
from PIL import Image
from glob import glob

def resize_images(image_path, search_key, new_im_size=(120,120)):
    all_image_paths = glob(os.path.join(image_path,search_key,'*'))
    print('[INFO] Resizing %d images for query: %s' % (len(all_image_paths), search_key))
    for im_path in all_image_paths:
        try:
            im = Image.open(im_path)        
            im.resize(new_im_size).save(im_path)
        except:
            print('[ERROR] Unable to resize image for query: %s' % search_key)


def worker_thread(search_key):
    image_scraper = GoogleImageScraper(
        webdriver_path, 
        image_path,
        search_key, 
        number_of_images, 
        headless, 
        min_resolution, 
        max_resolution, 
        max_missed)
    image_urls = image_scraper.find_image_urls()
    image_scraper.save_images(image_urls, keep_filenames)
    resize_images(image_path, search_key)

    #Release resources
    del image_scraper

if __name__ == "__main__":
    #Load in pokemon file
    pokemon = pd.read_csv('pokemon.csv')
    
    #Define file path
    webdriver_path = os.path.normpath(os.path.join(os.getcwd(), 'webdriver', webdriver_executable()))
    image_path = os.path.normpath(os.path.join(os.getcwd(), 'photos')) #Replace with path of root dir

    #Add new search key into array ["cat","t-shirt","apple","orange","pear","fish"]
    search_keys = list(set(('pokemon ' + pokemon.Name).values))

    #Parameters
    number_of_images = 100              # Desired number of images
    headless = True                     # True = No Chrome GUI
    min_resolution = (0, 0)             # Minimum desired image resolution
    max_resolution = (9999, 9999)       # Maximum desired image resolution
    max_missed = 50                     # Max number of failed images before exit
    number_of_workers = 16              # Number of "workers" used
    keep_filenames = False              # Keep original URL image filenames

    #Run each search_key in a separate thread
    #Automatically waits for all threads to finish
    #Removes duplicate strings from search_keys
    with concurrent.futures.ThreadPoolExecutor(max_workers=number_of_workers) as executor:
        executor.map(worker_thread, search_keys)