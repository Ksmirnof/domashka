from re import sub
from datetime import datetime
from dateutil.parser import parse as dateparse
from dateutil.relativedelta import relativedelta as datedelta
from matplotlib import pyplot as plt
import requests


class Vk:

    APIVER = '5.63'
    APIURI = 'https://api.vk.com/method'
    POSTS_MAXPART = 100
    COMMENTS_MAXPART = 100

    _userinfo_cache = dict()

    def _build_query(self, method, **kwargs):
        query = "%s/%s?v=%s" % (self.APIURI, method, self.APIVER)
        for key in kwargs:
            query += "&%s=%s" % (key, str(kwargs[key]))
        return query

    def _get_json(self, method, **kwargs):
        return requests.get(self._build_query(method, **kwargs)).json()

    def clear_cache(self):
        self._userinfo_cache = dict()

    def get_posts(self, domain, count=-1):
        r = self._get_json('wall.get', domain=domain, offset=0, count=1)
        if count == -1 or count > r['response']['count']:
            count = r['response']['count']
        offset = 0
        posts = list()

        while offset < count:
            need2read = count - offset
            if need2read > self.POSTS_MAXPART:
                need2read = self.POSTS_MAXPART
            posts.append(
                self._get_json('wall.get', domain=domain, offset=offset, count=need2read)
            )
            offset += need2read
        return posts

    def get_comments(self, page_owner_id, post_id, count=-1):
        r = self._get_json('wall.getComments', owner_id=page_owner_id, post_id=post_id, offset=0, count=1)
        if count == -1 or count > r['response']['count']:
            count = r['response']['count']
        offset = 0
        comments = list()

        while offset < count:
            need2read = count - offset
            if need2read > self.COMMENTS_MAXPART:
                need2read = self.COMMENTS_MAXPART
            comments.append(
                self._get_json('wall.getComments', owner_id=page_owner_id, post_id=post_id, offset=offset, count=need2read)
            )
            offset += need2read
        return comments

    def get_user_socinfo(self, user_id):
        if user_id in self._userinfo_cache:
            user = self._userinfo_cache[user_id]
        else:
            user = self._get_json('users.get', user_ids=user_id, fields='bdate,city')
            self._userinfo_cache.update({user_id: user})
        return user


def format_filename(s):
    return sub(r'[^\w()\.\-_ ]', '', s)


def get_age_from_bdate(bdate):
    try:
        return datedelta(datetime.today(), dateparse(bdate)).years
    except ValueError:
        return 0


def get_data(domain, max_posts=-1, max_comments=-1):
    vk = Vk()
    lengths = dict()
    comment_ages_lengths = dict()
    post_ages_lengths = dict()
    texts = dict()
    print("Downloading posts...")
    posts = vk.get_posts(domain, max_posts)
    print("Posts found: %d" % posts[0]['response']['count'])
    if max_posts > 0:
        p2p = max_posts
    else:
        p2p = posts[0]['response']['count']
    print("Posts to process max: %d" % p2p)
    for r_p in posts:
        print("\tProcessing next part...")
        for post in r_p['response']['items']:
            post_owner = post['owner_id']
            post_author = post['from_id']
            post_id = post['id']
            post_text = post['text']
            texts.update({post_id: {'text': post_text, 'comments': []}})
            post_len = len(post_text.split())

            if post_author > 0:
                post_user = vk.get_user_socinfo(post_author)
                if 'bdate' in post_user['response'][0]:
                    post_user_age = get_age_from_bdate(post_user['response'][0]['bdate'])
                else:
                    post_user_age = 0
                try:
                    post_user_city = post_user['response'][0]['city']['title']
                except KeyError:
                    post_user_city = None
                if post_user_age > 0 and post_user_city is not None:
                    if post_user_city not in post_ages_lengths:
                        post_ages_lengths.update({post_user_city: {post_user_age: post_len}})
                    elif post_user_age not in post_ages_lengths[post_user_city]:
                        post_ages_lengths[post_user_city].update({post_user_age: post_len})
                    else:
                        post_ages_lengths[post_user_city][post_user_age] = \
                            (post_ages_lengths[post_user_city][post_user_age] + post_len) / 2
            
            comments = vk.get_comments(post_owner, post_id, max_comments)
            comments_count = 0
            comments_total_len = 0
            for r_c in comments:
                print("\t\tProcessing comments...")
                for comment in r_c['response']['items']:
                    comment_id = comment['id']
                    comment_owner = comment['from_id']
                    comment_text = comment['text']
                    texts[post_id]['comments'].append({'id': comment_id, 'text': comment_text})
                    comment_len = len(comment_text.split())
                    comments_total_len += comment_len
                    comments_count += 1

                    if comment_owner > 0:
                        comment_user = vk.get_user_socinfo(comment_owner)
                        if 'bdate' in comment_user['response'][0]:
                            comment_user_age = get_age_from_bdate(comment_user['response'][0]['bdate'])
                        else:
                            comment_user_age = 0
                        try:
                            comment_user_city = comment_user['response'][0]['city']['title']
                        except KeyError:
                            comment_user_city = None
                        if comment_user_age > 0 and comment_user_city is not None:
                            if comment_user_city not in comment_ages_lengths:
                                comment_ages_lengths.update({comment_user_city: {comment_user_age: comment_len}})
                            elif comment_user_age not in comment_ages_lengths[comment_user_city]:
                                comment_ages_lengths[comment_user_city].update({comment_user_age: comment_len})
                            else:
                                comment_ages_lengths[comment_user_city][comment_user_age] = \
                                    (comment_ages_lengths[comment_user_city][comment_user_age] + comment_len) / 2

            if comments_count > 0:
                comments_avg_len = comments_total_len / comments_count
                if post_len not in lengths:
                    lengths.update({post_len: comments_avg_len})
                else:
                    lengths[post_len] = (lengths[post_len] + comments_avg_len) / 2

    return (texts, lengths, comment_ages_lengths, post_ages_lengths)


def draw_lengths(lengths, show=False):
    X = list()
    Y = list()
    sorted_lengths = list(lengths.keys())
    sorted_lengths.sort()
    for post_len in sorted_lengths:
        X.append(post_len)
        Y.append(lengths[post_len])
    plt.plot(X, Y, c='blue', marker='o')
    plt.xlim(0, X[len(X)-1]+5)
    plt.ylim(0, max(Y)+5)
    plt.title("Соотношение длины поста к средней длине комментария")
    plt.xlabel("Длина поста")
    plt.ylabel("Средняя длина комментария")
    plt.savefig('lengths.png')
    if show:
        plt.show()
    plt.clf()


def draw_ages_common(comment_ages_lengths, post_ages_lengths, show=False):

    comments = dict()
    for city in comment_ages_lengths:
        for com in comment_ages_lengths[city]:
            if com not in comments:
                comments.update({com: comment_ages_lengths[city][com]})
            else:
                comments[com] = (comments[com] + comment_ages_lengths[city][com]) / 2

    X1 = list()
    Y1 = list()
    for com_age in comments:
        X1.append(com_age)
        Y1.append(comments[com_age])

    posts = dict()
    for city in post_ages_lengths:
        for com in post_ages_lengths[city]:
            if com not in posts:
                posts.update({com: post_ages_lengths[city][com]})
            else:
                posts[com] = (posts[com] + post_ages_lengths[city][com]) / 2

    X2 = list()
    Y2 = list()
    for post_age in posts:
        X2.append(post_age)
        Y2.append(posts[post_age])

    plt.scatter(X1, Y1, c='blue', marker='o', label='Комментарии')
    plt.scatter(X2, Y2, c='red', marker='^', label='Посты')
    plt.xlim(0, max(X1+X2)+5)
    plt.ylim(0, max(Y1+Y2)+5)
    plt.title("Соотношение возраста и длины постов и комментариев")
    plt.xlabel("Возраст")
    plt.ylabel("Средняя длина")
    plt.legend()
    plt.savefig('ages_common.png')
    if show:
        plt.show()
    plt.clf()


def draw_comment_ages_cities(comment_ages_lengths, show=False):
    for city in comment_ages_lengths:
        X = list()
        Y = list()
        for com in comment_ages_lengths[city]:
            X.append(com)
            Y.append(comment_ages_lengths[city][com])
        plt.scatter(X, Y, c='blue', marker='o')
        plt.xlim(0, max(X) + 5)
        plt.ylim(0, max(Y) + 5)
        plt.title("Соотношение возраста и длины комментариев в г. %s" % city)
        plt.xlabel("Возраст")
        plt.ylabel("Средняя длина")
        plt.savefig(format_filename("ages_comment_%s.png" % city))
        if show:
            plt.show()
        plt.clf()


def draw_post_ages_cities(post_ages_lengths, show=False):
    for city in post_ages_lengths:
        X = list()
        Y = list()
        for post in post_ages_lengths[city]:
            X.append(post)
            Y.append(post_ages_lengths[city][post])
        plt.scatter(X, Y, c='red', marker='^')
        plt.xlim(0, max(X) + 5)
        plt.ylim(0, max(Y) + 5)
        plt.title("Соотношение возраста и длины постов в г. %s" % city)
        plt.xlabel("Возраст")
        plt.ylabel("Средняя длина")
        plt.savefig(format_filename("ages_post_%s.png" % city))
        if show:
            plt.show()
        plt.clf()

(texts, lengths, comment_ages_lengths, post_ages_lengths) = \
    get_data('dormitory8hse', 300, 300)

with open('texts.log', 'wb') as f:
    f.write(bytes(repr(texts), 'utf-8'))
with open('lengths.log', 'wb') as f:
    f.write(bytes(repr(lengths), 'utf-8'))
with open('comment_ages_lengths.log', 'wb') as f:
    f.write(bytes(repr(comment_ages_lengths), 'utf-8'))
with open('post_ages_lengths.log', 'wb') as f:
    f.write(bytes(repr(post_ages_lengths), 'utf-8'))

if len(lengths) > 0:
    draw_lengths(lengths)
if len(comment_ages_lengths) > 0:
    draw_comment_ages_cities(comment_ages_lengths)
if len(post_ages_lengths) > 0:
    draw_post_ages_cities(post_ages_lengths)
if len(comment_ages_lengths) > 0 and len(post_ages_lengths) > 0:
    draw_ages_common(comment_ages_lengths, post_ages_lengths)
