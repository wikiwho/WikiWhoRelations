import requests
import csv

from WikiWho.wikiwho import Wikiwho


def process_api_output(page_id, title):

    url = 'https://en.wikipedia.org/w/api.php'
    params = {'pageids': page_id, 'action': 'query', 'prop': 'revisions',
              'rvprop': 'content|ids|timestamp|sha1|comment|flags|user|userid',
              'rvlimit': 'max', 'format': 'json', 'continue': '', 'rvdir': 'newer'}

    wikiwho = Wikiwho(title)
    while True:
        # gets only first 50 revisions of given page
        if wikiwho.rvcontinue != '0':
            params['rvcontinue'] = wikiwho.rvcontinue
        result = requests.get(url=url, params=params).json()
        if 'error' in result:
            raise Exception('Wikipedia API returned the following error:' + str(result['error']))
        pages = result['query']['pages']
        if "-1" in pages:
            raise Exception('The article ({}) you are trying to request does not exist!'.format(page_id))

        _, page = result['query']['pages'].popitem()
        if 'missing' in page:
            raise Exception('The article ({}) you are trying to request does not exist!'.format(page_id))

        wikiwho.analyse_article(page.get('revisions', []))
        if 'continue' not in result:
            break
        wikiwho.rvcontinue = result['continue']['rvcontinue']
    return wikiwho


from WikiWho.utils import iter_rev_tokens

def printDyads(wikiwho):

    header = ["s_revision", "s_author", "t_revision", "t_author", "deleted(-,out)", "undo_reintro(-,out)", "undo_delete(-,in)", "reintroduced(+,in)", "redeleted(+,out)", "oadds(=,in)"#, 'is_vandalism'
    ]

    print("\t".join(header))

    #for (revision, vandalism) in wikiwho.ordered_revisions:
    for revision in wikiwho.ordered_revisions:
        if revision in wikiwho.spam_ids:
             continue
        relation = wikiwho.relations[revision]
        revision_obj = wikiwho.revisions[revision]

        targets = set(relation.deleted.keys()) | set(relation.undo_reintro.keys()) | set(relation.undo_delete.keys()) | set(relation.reintroduced.keys()) | set(relation.redeleted.keys()) #with self_ ? then include these: | set(relation.self_deleted.keys()) | set(relation.self_undo_reintro.keys()) | set(relation.self_undo_delete.keys()) | set(relation.self_reintroduced.keys()) | set(relation.self_redeleted.keys())

        #print targets
        for target in targets:
             print(str(revision_obj.id) + "\t" + str(revision_obj.editor) + "\t" + str(target) + "\t" + str(wikiwho.revisions[target].editor) + "\t" + str(relation.deleted.get(target, [])) + "\t" + str(relation.undo_reintro.get(target, [])) + "\t" + str(relation.undo_delete.get(target, [])) + "\t" + str(relation.reintroduced.get(target, []))+ "\t" + str(relation.redeleted.get(target, []))  + "\t" + str(relation.added)#  + "\t" +  str(relation.is_vandalism)
             )

if __name__ == '__main__':

    title = 'Technology'
    page_id = 29816

    wikiwho_obj = process_api_output(page_id, title)

    printDyads(wikiwho_obj)
