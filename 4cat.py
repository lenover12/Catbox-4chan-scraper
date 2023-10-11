import os
import re
import time
import aiohttp
import asyncio

# all lists that can be changed will have the text #CHANGE-ME above them
# to remove an entry from the list, delete the word that is surrounded
# by " " or ' ' and one comma before or after the word.
# example: ["Diffusion ","DEGENerated ", "/AI/ " " AI "] = ["Diffusion ", "/AI/ " " AI "]

#CHANGE-ME
#search terms:
thread_titles = ["Diffusion ","DEGENerated ", "/AI/ ", " AI "]

save_dir = './catbox/'
if not os.path.exists(save_dir):
    os.mkdir(save_dir)

visited_sites_doc = 'visited_sites.txt'
if not os.path.exists(visited_sites_doc):
    f = open(visited_sites_doc, 'w')
    f.close()

#also target threads in archive?
#WIP -- do not set to true as it will scrape far more than stable diffusion creations
scrape_archive = False

#how many files downloaded
download_count = 0

def ascii_cise():
    print ("                      ____...                                  ")
    print ("             .-\"--\"\"\"\".__    `.                                ")
    print ("            |            `    |                                ")
    print ("  (         `._....------.._.:                                 ")
    print ("   )         .()''        ``().                                ")
    print ("  '          () .=='  `===  `-.                                ")
    print ("   . )       (         g)                                      ")
    print ("    )         )     /        J                                 ")
    print ("   (          |.   /      . (                                  ")
    print ("   $$         (.  (_'.   , )|`                                 ")
    print ("   ||         |\`-....--'/  ' \                                ")
    print ("  /||.         \\\\ | | | /  /   \.                              ")
    print (" //||(\         \`-===-'  '     \o.                            ")
    print (".//7' |)         `. --   / (     OObaaaad888b.                 ")
    print ("(<<. / |     .a888b`.__.'d\     OO888888888888a.               ")
    print (" \  Y' |    .8888888aaaa88POOOOOO888888888888888.              ")
    print ("  \  \ |   .888888888888888888888888888888888888b              ")
    print ("   |   |  .d88888P88888888888888888888888b8888888.             ")
    print ("   b.--d .d88888P8888888888888888a:f888888|888888b             ")
    print ("   88888b 888888|8888888888888888888888888\8888888             ")

#file types to download (has not been tested for zip or rar or anything besides what is default)
async def download_files(urls):
    png_pat = re.compile(r'https://files\.catbox\.moe/[a-z0-9]{6}\.png')
    jpg_pat = re.compile(r'https://files\.catbox\.moe/[a-z0-9]{6}\.jpg')
    jpeg_pat = re.compile(r'https://files\.catbox\.moe/[a-z0-9]{6}\.jpeg')
    txt_pat = re.compile(r'https://files\.catbox\.moe/[a-z0-9]{6}\.txt')
    gif_pat = re.compile(r'https://files\.catbox\.moe/[a-z0-9]{6}\.gif')
    # zip_pat = re.compile(r'https://files\.catbox\.moe/[a-z0-9]{6}\.zip')
    # rar_pat = re.compile(r'https://files\.catbox\.moe/[a-z0-9]{6}\.rar')


    async with aiohttp.ClientSession() as session:
        visited_sites = set()
        with open(visited_sites_doc, 'r') as f:
            for line in f:
                visited_sites.add(line.strip())
        tasks = []
        for url in urls:
            # Loop through the thread URLs passed in as an argument
            response = await session.get(url)
            # Images
            matches = re.findall(png_pat,  await response.text()) + re.findall(jpg_pat,  await response.text()) + re.findall(jpeg_pat,  await response.text()) + re.findall(txt_pat,  await response.text()) + re.findall(gif_pat,  await response.text())
            for match in matches:
                tasks.append(asyncio.create_task(download_file(session, match, visited_sites)))

        await asyncio.gather(*tasks)
                    

# Download everything
async def download_file(session, url, visited_sites):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    }
    try:
        async with session.get(url, headers=headers) as response:
            content = await response.read()
            filename = os.path.basename(url)
            if url not in visited_sites:
                print("downloading " + str(filename).upper())
                with open(os.path.join(save_dir, filename), 'wb') as f:
                    f.write(content)
                visited_sites.add(url)
                global download_count
                download_count = download_count + 1
                with open(visited_sites_doc, "a") as file:
                    file.write(url + "\n")
    except Exception as e:
        print(f'Error downloading {url}: {e}')

#CHANGE-ME
async def main():
    boards = ['a','c','w','m','cgl','cm','n','jp','vt','v','vg','vm','vmg','vp','vr','vrpg','vst','co','g','tv','k','o','an','tg','sp','xs','pw','sci','his','int','out','toy','i','po','p','ck','ic','wg','lit','mu','fa','3','gd','diy','wsg','qst','biz','trv','fit','x','adv','lgbt','mlp','news','wsr','vip','r9k','pol','bant','soc','s4s','s','hc','hm','h','e','u','d','y','t','hr','gif','aco','r']
    # 'trash' & 'b' was removed as it's f*cking gross

    start_time = time.time()

    ascii_cise()

    async with aiohttp.ClientSession() as session:
        for board in boards:
            # Start off with the basic requests and all that 
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
            }
            async with session.get(f"https://a.4cdn.org/{board}/catalog.json", headers=headers) as response:
                catalog = await response.json()
            post_numbers = []

            # Iterate over the pages in the catalog to get the desired threads
            # Change the search string as desired
            for page in catalog:
                for thread in page["threads"]:
                    for thread_title in thread_titles:
                        if "sub" in thread and re.search(r""+thread_title, thread["sub"], re.IGNORECASE):
                            post_numbers.append(thread["no"])
            
            if (scrape_archive):
                async with session.get(f"https://a.4cdn.org/{board}/archive.json", headers=headers) as response:
                    archive = await response.json()
                for no in archive:
                    post_numbers.append(no)

            if (post_numbers):
                print("board /" + str(board) + "/ threads:\n" + str(post_numbers))

            # Transform the post_numbers into a list of URLs
            urls = ["https://boards.4chan.org/{}/thread/{}".format(board, post_number) for post_number in post_numbers]
            
            await download_files(urls)
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    global download_count
    if download_count >= 1:
        print(f'{download_count} files downloaded successfully in {elapsed_time:.2f} seconds.')
        try:
            print(f'{download_count / elapsed_time:.2f} files & or images/s')
        except ZeroDivisionError:
            pass

loop = asyncio.get_event_loop()
loop.run_until_complete(main())