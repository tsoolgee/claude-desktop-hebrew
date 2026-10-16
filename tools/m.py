import json,glob,sys
n=sys.argv[1]
d={}
for f in sorted(glob.glob(f'out_{n}_*.json')): d.update(json.load(open(f,encoding='utf-8')))
json.dump(d,open(f'out_{n}.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
