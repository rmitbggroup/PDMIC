import argparse
import sys
import math
import networkx as nx
import random
import time
import Binary
import Flexible
import copy
def parse_args():
	parser = argparse.ArgumentParser(description="profit divergence minimization")

	parser.add_argument('--degree', nargs='?', default='degree/LastFM', help='input graph file')

	parser.add_argument('--dis', nargs='?', default='Uniform', help='sampling distributions with a specific focus. Choices: Macro, Micro, Nano, Uniform.')

	parser.add_argument('--load', type=int, default='90',help='the number of candidates')

	parser.add_argument('--budgetRatio', type=float, default='0.8',help='the budget = budgetRatio * total influence spread of candidates')

	parser.add_argument('--expectRatio', type=float, default='0.5',
			help='the weighted influence is sampled from [1 * delta,  (1+expectRatio)*delta]')

	parser.add_argument('--numPieces', type=float, default='10',
			help='the size of integer price choice set for fc-exact')	

	parser.add_argument('--degreeRatio', type=float, default='0.2',
			help='the ratio of degrees of influencers belonging to the same tier over the total degree of all users in the network')	

	parser.add_argument('--cutPoint', type=float, default='0.5',
			help='the price choice set R is generated from the range [(1-cutpoint)*delta, (1+cutpoint)*delta]')	

	parser.add_argument('--method', nargs='?', default='BCExact',help='BCExact,BCMG,ICExact,CRInf,CRMWS.')		
	
	parser.add_argument('--output', nargs='?', default='output/',help='default output folder')
	
	parser.add_argument('--seed', type=int, default='10',help='random seed')

	parser.add_argument('--version', type=int, default='0',help='0 for float version of FCInfGreedy and 1 for integer version')
	
	parser.add_argument('--infmax', type=int, default='0',help='0 refers to BCExact with profit minimization, and 1 refers to BCExact with influence maximization')
	return parser.parse_args()

seeds={}

seeds['Dogster']=123
seeds['Orkut']=234
seeds['Instagram']=345
seeds['Tiktok']=567
seeds['Gowalla']=678
seeds['LastFM']=8910
seeds['Hamster']=91011

Dis={}
Dis["Macro"]=(0.5,0.25,0.25)
Dis["Micro"]=(0.25,0.5,0.25)
Dis["Nano"]=(0.25,0.25,0.5)
Dis["Uniform"]=(0.33,0.33,0.33)


def getCuts(inf_profit,degreeRatio):
	cuts=[]
	percentage=[degreeRatio*1,degreeRatio*2,degreeRatio*3,2]
	degreeCul=0
	totalDegree=0
	for inf in inf_profit:
		totalDegree=totalDegree+inf[1]

	index=0
	for i in range(len(inf_profit)):
		degreeCul=degreeCul+inf_profit[i][1]
		if (float(degreeCul)/totalDegree>percentage[index]):
			cuts.append(i) 
			index=index+1
		if (index==len(percentage)-1):
			break

	#print (str(float(cuts[0])/len(inf_profit))+" "+str(float(cuts[1])/len(inf_profit))+" "+str(float(cuts[2])/len(inf_profit)))
	return cuts


def f(cost, expect):
	if (cost<expect):
		return cost
	else:
		return (2*expect-cost)


def BinaryChoices(inf_profit,Budgets,args):

	B=Budgets[0]
	
	if (args.infmax==1):
		Binary.BCDP(B, inf_profit,args)
	elif (args.version==1):
		Flexible.FCInfGreedy(Budgets,inf_profit,args)
	else:		
		Binary.BCDP(B, inf_profit,args)

		Binary.BCGreedy(B, inf_profit,args)

		Flexible.FCInfGreedy(Budgets,inf_profit,args)

		Flexible.FCMWSGreedy(inf_profit,Budgets,args)

#inf_profit
def FlexibleChoices(inf_profit,Budgets,args):	
	
	
	Flexible.FCDP(Budgets[0],inf_profit,args)
	

	
def main(args):
	seed=args.seed
	dataset=args.degree.split("/")[-1]
	if (dataset in seeds):
		seed=seeds[dataset]

	random.seed(seed)
	inf_profit=[]

	index=-1
	with open(args.degree) as f:	
		for line in f:
			index+=1
			#print(index)
			strlist = line.split()
			degree=int(strlist[0])
			inf_profit.append([index,degree])

	inf_profit=list(inf_profit)
	inf_profit=sorted( inf_profit, key=lambda ele: (-ele[1]) )

	
	#categorize influencers
	cuts=getCuts(inf_profit,args.degreeRatio)

	# end index of different tiers
	macro=cuts[0]
	micro=cuts[1]
	nano=cuts[2]

	macroSize=int(args.load*Dis[args.dis][0])
	microSize=int(args.load*Dis[args.dis][1])
	nanoSize=int(args.load*Dis[args.dis][2])
	if (macroSize+microSize+nanoSize <args.load):
		macroSize=macroSize+1

	# sampling candidates
	candidates=[]
	candidates.extend( random.sample(inf_profit[0:macro], macroSize  ) )
	candidates.extend( random.sample(inf_profit[macro:micro], microSize  ) )
	candidates.extend( random.sample(inf_profit[micro:nano], nanoSize  ) )

	inf_profit=candidates
	inf_profit=sorted( inf_profit, key=lambda ele: (-ele[1]) )

	totaldegree=0

	for inf in inf_profit:
		totaldegree=totaldegree+inf[1]
	
	B=0

	for inf in inf_profit:
		B=B+inf[1]

	B=int(B*args.budgetRatio)


	# generate profit expectation
	influenceVariance=[]
	
	for inf in inf_profit:
		ratio=float(random.uniform(0, args.expectRatio)) +1 
		influenceVariance.append(int(ratio*inf[1]))


	tempB=0
	profitRatio=[]

	for inf in influenceVariance:
		tempB=tempB+inf


	for inf in influenceVariance:
		profitRatio.append( float(inf)/tempB )

	profit=0
	for i in range(len( inf_profit  )):
		inf_profit[i].append(int( round(profitRatio[i]*B)))
		profit=profit+ int( round(profitRatio[i]*B))

	B=profit

	if (args.infmax==1):
		for inf in inf_profit:
			inf[2]=inf[1]

	Budgets=[]


	Budgets.append(B)

	total=0

	for b in Budgets:
		total=total+b
	
	if (args.method=="BCExact"):
		Binary.BCDP(Budgets[0], inf_profit,args)

	if (args.method=="BCMG"):
		Binary.BCGreedy(Budgets[0], inf_profit,args)

	if (args.method=="ICExact"):	
		Flexible.FCDP(Budgets[0],inf_profit,args)

	if (args.method=="CRInf"):	
		Flexible.FCInfGreedy(Budgets,inf_profit,args)

	if (args.method=="CRMWS"):		
		Flexible.FCMWSGreedy(Budgets,inf_profit,args)




if __name__ == "__main__":
	args = parse_args()
	main(args)
