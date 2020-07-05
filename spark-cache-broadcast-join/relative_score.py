from pyspark import SparkConf, SparkContext
import sys
import json

assert sys.version_info >= (3, 5)

def add_pairs(x, y):
    return (x[0] + y[0], x[1] + y[1])

def get_avg(x):
    redd = x[0]
    count, score = x[1]
    return (redd,(float(score)/count))

def check_key(parse_json):
    if 'subreddit' not in parse_json or 'score' not in parse_json:
        return(None)
    else:
        return(parse_json['subreddit'],(1,parse_json['score']))

def get_author_score(kv):
    sub = kv[0]
    average, comment = kv[1] 
    if 'author' not in comment:
        return(None)
    else:
        return(comment['score']/average, comment['author'])  

def get_key(kv):
    return kv[0]       

def main(inputs, output):
    in_json = sc.textFile(inputs)
    parse_json = in_json.map(json.loads).cache()
    objs = parse_json.map(check_key).filter(lambda val : val != None)
    agg = objs.reduceByKey(add_pairs)
    average = agg.map(get_avg).filter(lambda x : x[1]>0)
    commentbysub = parse_json.map(lambda c: (c['subreddit'], c))
    join_all = average.join(commentbysub)
    output_rdd = join_all.map(get_author_score).filter(lambda val : val != None)
    output_rdd.sortBy(get_key,ascending=False).map(json.dumps).saveAsTextFile(output)

if __name__ == '__main__':
    conf = SparkConf().setAppName('reddit average')
    sc = SparkContext(conf=conf)
    assert sc.version >= '2.3'
    inputs = sys.argv[1]
    output = sys.argv[2]
    main(inputs, output)

