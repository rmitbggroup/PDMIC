import sys   
import MPD
import math
import copy
import time
import random
import os

def FCDP(B,org_inf_profit,args):
	inf_profit=copy.deepcopy(org_inf_profit)

	inf_profit=sorted(inf_profit, key=lambda ele: (ele[1]))
	#print (inf_profit)
	start=time.time()
	rangecosts=[]

	for inf in inf_profit:
		pace=max(1,int(inf[1]*2*args.cutPoint/args.numPieces))
		s=int(inf[1]*(1-args.cutPoint))+1
		e=int(inf[1]*(1+args.cutPoint))
		l=list(range( s,e,pace))
		l.append(inf[1])
		l.sort()
		rangecosts.append(l)
	
	tracking=[]

	for i in range(len(inf_profit)):
		# X (previous node id, budget, price)
		layer=[{X: (-1,-1,-1) for X in rangecosts[i]} for b in range(B+1)]
		tracking.append(layer)


	results=[]
	layer = [{X: -sys.maxsize for X in rangecosts[0]} for b in range(B+1)]
	results.append(layer)

	
	for b in range(B+1):
		for cost in rangecosts[0]:
			if (cost <=b):
				results[0][b][cost]=MPD.f(cost,inf_profit[0][2])

	for k in range(1, len(inf_profit)):
		startb=rangecosts[k][0]
		if (k==len(inf_profit)):
			startb=B
		layer=[{X: -sys.maxsize for X in rangecosts[k]} for b in range(B+1)]
		results.append(layer)

		for b in range (startb,B+1):
			for cost in rangecosts[k]:
				
				if (cost>b):
					break
				elif (cost==b):
					results[k][b][cost]=MPD.f(cost,inf_profit[k][2])
					break
					#gain=float(inf_profit[k][1])/cost
				else:
					results[k][b][cost]=MPD.f(cost,inf_profit[k][2])

				for i in range(k):
					if (inf_profit[i][1]==inf_profit[k][1]):
							
							if (not cost in results[i][b-cost] ):
								continue
							value=MPD.f(cost,inf_profit[k][2])+results[i][b-cost][cost]
							#results[k][b][cost]=max(results[k][b][cost],value)
							if (value>results[k][b][cost]):
								results[k][b][cost]=value
								tracking[k][b][cost]=(i,(b-cost),cost)
							continue

					for index in range(len(rangecosts[i])):
						pcost=rangecosts[i][index]
					
						if (b-cost < pcost):
							break
						#if ( lowercost <= pcost):
						if (float(inf_profit[i][1])/pcost -float(inf_profit[k][1])/cost<0.0001):
								value=MPD.f(cost,inf_profit[k][2])+results[i][b-cost][pcost]
								
								if (value>results[k][b][cost]):

									results[k][b][cost]=value
									tracking[k][b][cost]=(i,(b-cost),pcost)									
						
	best=0
	end=(-1,-1,-1)
	for k in range(len(inf_profit)):
		inf_profit[k].append(0)
		for cost in rangecosts[k]:
			value=results[k][B][cost]
			if (value>best):
				best=value
				end=(k,B,cost)

	inf_profit[end[0]][-1]=end[2]

	while( not tracking[end[0]][end[1]][end[2]][0]==-1):
		pointer=tracking[end[0]][end[1]][end[2]]
		end=pointer
		inf_profit[pointer[0]][-1]=pointer[2]

	realtime=time.time()-start
	print ("FCDP: numPieces:"+str(args.numPieces)+",divergence:"+str(B-best)+",D-ratio:"+str(float(B-best)/B)+", time cost (s):"+str(realtime))


	inf_profit=sorted( inf_profit, key=lambda ele: (-ele[1]) )

	filename=args.output+args.degree.split("/")[-1]+"/FCDP/"+"load_"+str(args.load)+"_br_"+str(args.budgetRatio)+"_pieces_"+str(args.numPieces)+"_cut_"+str(args.cutPoint)+"_dis_"+str(args.dis)

	os.makedirs(os.path.dirname(filename), exist_ok=True)
	with open(filename, "w") as f:
		count=0
		while(count<4):
			for inf in inf_profit:
				f.write(str(inf[count])+" ")
			f.write("\n")
			count=count+1
		f.write(str(realtime))

	return best

def BestPrice(inputBudgetRange, residues, expectation):
	profitScores={}

	costRecords={}

	quaple=[]


	for i in range(len(residues)):
		feasibleBudgetRange=[]
		if (residues[i]<inputBudgetRange[0]):
			profitScores[i]=-sys.maxsize
			costRecords[i]=-sys.maxsize
			continue
		feasibleBudgetRange.append(inputBudgetRange[0])

		if (residues[i]<=inputBudgetRange[1]):
			feasibleBudgetRange.append(residues[i])

		else:
			feasibleBudgetRange.append(inputBudgetRange[1])

	

		if (expectation<= feasibleBudgetRange[0]):
			#print(feasibleBudgetRange[0])
			profitScores[i]=MPD.f(feasibleBudgetRange[0],expectation)
			costRecords[i]=feasibleBudgetRange[0]
		elif (feasibleBudgetRange[0] < expectation and expectation<=feasibleBudgetRange[1] ):
			profitScores[i]=expectation
			costRecords[i]=expectation
		else:
			profitScores[i]=MPD.f(feasibleBudgetRange[1],expectation)
			costRecords[i]=feasibleBudgetRange[1]

		quaple.append( (i,profitScores[i],costRecords[i], residues[i]  ) )

		
	quaple=sorted(quaple, key=lambda ele: (-ele[1], -ele[3]))

	return quaple	


def FCInfGreedy(Budgets,org_inf_profit,args):
	seedSet=[]
	seedCost={}
	residues=[]
	totalScore=0
	zeroCount=0
	records=[]
	usedBudget=0
	totalBudget=0

	
	#tempinf_profit=sorted(org_inf_profit, key=lambda ele: (-ele[1]))	
	tempinf_profit=copy.deepcopy(org_inf_profit)
	tempinf_profit=sorted(tempinf_profit, key=lambda ele: (-ele[1]))	

	start=time.time()
	for inf in tempinf_profit:
		inf.append(float(inf[1])/inf[2])

	reorder=[]

	for i in range(len(tempinf_profit)):
		if(tempinf_profit[i][3]==1):
			reorder.append(i)


	reorderSet=set(reorder)

	for i in range(len(tempinf_profit)):
		if (i not in reorderSet):
			reorder.append(i)

	inf_profit=[]


	for i in reorder:
		inf_profit.append(tempinf_profit[i])


	for b in Budgets:
		residues.append(b)
		totalBudget=totalBudget+b


	rangecosts=[]


	for inf in inf_profit:
		'''
		lowerc=max(1,int( (1-alpha) * inf[2] ))
		upperc=min(int( (1+alpha) * inf[2] ),totalBudget)
		'''
		
		lowerc=0
		upperc=totalBudget	
		rangecosts.append([lowerc,upperc])	
		
		
		#rangecosts.append([0,Budgets[0]])
		
	for index in range(len(inf_profit)):
		if (index in seedCost):
			continue
		upperb=max(residues)
		inf=inf_profit[index][1]
	#for inf in influence:
		lowerb=1

		if (not len(seedSet)==0):
			foundequal=False
			equalIndex=-1

			minInf=sys.maxsize
			foundlowerb=False
			minIndex=-1
			
			maxInf=0
			foundupperb=False
			maxIndex=-1

			for index2 in seedSet:
				seedInf=inf_profit[index2][1]
				if (seedInf == inf):
					foundequal=True
					equalIndex=index2
					break
				if (seedInf > inf):
					if(seedInf < minInf):
						foundlowerb=True
						minIndex=index2
						minInf=seedInf

				if (seedInf < inf):
					if(seedInf > maxInf):
						foundupperb=True
						maxInf=seedInf
						maxIndex=index2

			if (foundequal):
				lowerb=upperb=seedCost[equalIndex]
			else:
				if(foundlowerb):
					if (args.version==1):
						lowerb=int(  math.ceil(float(inf)/minInf*seedCost[minIndex]) )
					else:
						lowerb=float(inf)/minInf*seedCost[minIndex]
				if(foundupperb):
					if (args.version==1):
						tightupperb=int(  math.floor(float(inf)/maxInf*seedCost[maxIndex]) )	
					else:
						tightupperb=float(inf)/maxInf*seedCost[maxIndex]
					
					if (tightupperb<upperb):
						upperb=tightupperb

		if (lowerb>upperb):
			continue
			
		if (rangecosts[index][0]>upperb or rangecosts[index][1]<lowerb):
				continue
		if (rangecosts[index][0]>lowerb):
			lowerb=rangecosts[index][0]
		if (rangecosts[index][1]<upperb):
			upperb=rangecosts[index][1]

		feasibleBudgetRange=[lowerb,upperb]


		#print ("feasible range :"+str(feasibleBudgetRange)+", orignal range:"+str(rangecosts[index]))

		#print ("ranges "+str(feasibleBudgetRange)+",expectation "+str(expectations[inf])+",influence "+str(inf))
		quaple=BestPrice(feasibleBudgetRange, residues, inf_profit[index][2])

		if (len(quaple)==0):
			continue

		budgetIndex=quaple[0][0]
		score=quaple[0][1]
		finalcost=quaple[0][2]

	
		totalScore=totalScore+score
		seedCost[index]=finalcost
		seedSet.append(index)
		residues[budgetIndex]=residues[budgetIndex]-finalcost
		usedBudget=usedBudget+finalcost

		records.append( (  inf_profit[index][1] ,inf_profit[index][1]/finalcost, inf_profit[index][2],finalcost, score) )
	

		if (residues[budgetIndex]==0):
			zeroCount=zeroCount+1

		if(zeroCount==len(residues)):
			break	

	realtime=time.time()-start
	print ("FCInfGreedy: divergence:"+str(totalBudget-totalScore)+",D-ratio:"+str(float(totalBudget-totalScore)/totalBudget)+", time cost (s):"+str(realtime))


	for inf in inf_profit:
		inf.append(0)

	for i in seedSet:
		inf_profit[i][-1]=seedCost[i]


	filename=args.output+args.degree.split("/")[-1]+"/FCInfGreedy/"+"load_"+str(args.load)+"_br_"+str(args.budgetRatio)+"_dis_"+str(args.dis)
	if (args.version==1):
		filename=args.output+args.degree.split("/")[-1]+"/FCInfGreedy/"+"load_"+str(args.load)+"_br_"+str(args.budgetRatio)+"_dis_"+str(args.dis)+"_Int"
	os.makedirs(os.path.dirname(filename), exist_ok=True)
	with open(filename, "w") as f:
		count=0
		while(count<4):
			for inf in inf_profit:			
				
				if (count==3):
					f.write(str(inf[-1])+" ")
				else:
					f.write(str(inf[count])+" ")
			f.write("\n")
			count=count+1		
		f.write(str(realtime))	

	return totalScore,usedBudget


def LDSCompute(LDS,inf_profit):
	for i in range(len(inf_profit)):
		for k in range(i):
			if (LDS[k]+inf_profit[i][2] >LDS[i]):
				if (inf_profit[i][1]==inf_profit[k][1] and inf_profit[i][3] == inf_profit[k][3]):
					LDS[i] = LDS[k] + inf_profit[i][2]
				if (inf_profit[i][1]<inf_profit[k][1] and inf_profit[i][3] <= inf_profit[k][3]):
					LDS[i] = LDS[k] + inf_profit[i][2]



def getSequence( inf_profit,LDS,fullyUsedBudget,end,nodeSequenceIds):
	if (fullyUsedBudget>0):
		index=end
		if (index== (len(inf_profit)-1) ):
			while( not LDS[index]==fullyUsedBudget):
				index=index-1
		else:
			for h in range((end-1),-1,-1):
				if (LDS[h]==fullyUsedBudget):
					if(inf_profit[h][1]==inf_profit[end][1] and inf_profit[h][2]==inf_profit[end][2]):
						index=h
						break
					elif( (not inf_profit[h][1]==inf_profit[end][1]) and inf_profit[h][3]>=inf_profit[end][3]):
						index=h
						break

		nodeSequenceIds.append(index)

		getSequence(inf_profit, LDS, fullyUsedBudget-inf_profit[index][2],index,nodeSequenceIds)
		




def FCMWSGreedy(Budgets,org_inf_profit,args):

	
	 #**************************************************
	inf_profit=copy.deepcopy(org_inf_profit)
	
	start=time.time()
	sys.setrecursionlimit(1000000)

	for inf in inf_profit:
		inf.append(float(inf[1])/inf[2])

	inf_profit=sorted( inf_profit, key=lambda ele: (-ele[1],-ele[3]) )

	B=0


	for b in Budgets:
		B=B+b

	budget=B
	totalScore=0
	
	LDS=[inf_profit[i][2] for i in range(len(inf_profit))]
	LDSCompute(LDS,inf_profit)

	fullyUsedBudget=max(LDS)

	totalScore=totalScore+fullyUsedBudget
	B=B-fullyUsedBudget

	nodeSequenceIds=[]

	getSequence(inf_profit ,LDS,fullyUsedBudget,len(inf_profit)-1,nodeSequenceIds)

	nodeSequenceIds.sort()

	ratioAdjust=[]

	check=[] # (inf, inf/cost, cost, score, expect, node id)

	for node in nodeSequenceIds:
		check.append([inf_profit[node][1], inf_profit[node][3],inf_profit[node][2], inf_profit[node][2] , inf_profit[node][2],node ])


	minL=min(nodeSequenceIds)
	maxL=max(nodeSequenceIds)

	for i in range(minL):
		cost=inf_profit[i][1]/inf_profit[minL][3]
		score=MPD.f(cost, inf_profit[i][2])
		ratioAdjust.append( [i,cost,score, float(score)/cost,inf_profit[i][1]] )			

	for i in range(maxL+1,len(inf_profit)):
		cost=inf_profit[i][1]/inf_profit[maxL][3]
		score=MPD.f(cost, inf_profit[i][2])
		ratioAdjust.append( [i,cost,score, float(score)/cost,inf_profit[i][1]] )

	for j in range(0, len(nodeSequenceIds)-1):

		l=nodeSequenceIds[j]
		r=nodeSequenceIds[j+1]
		#print ("("+str(l-1)+","+str(r)+")")

		performanceRatio=inf_profit[r][3]
		lower_is_upper=False
		for i in range((r-1),l,-1):
		
			if (not lower_is_upper):
				if (inf_profit[i][1]==inf_profit[l][1]):
					performanceRatio=inf_profit[l][3]

				elif (not (inf_profit[i][1]==inf_profit[i+1][1])):
					if (float(inf_profit[i][1])/inf_profit[i][2]> float(inf_profit[l][1])/inf_profit[l][2]):
						performanceRatio=inf_profit[l][3]
						lower_is_upper=True

			cost=inf_profit[i][1]/performanceRatio
			score=MPD.f(cost, inf_profit[i][2])
			ratioAdjust.append( [i,cost,score, float(score)/cost,inf_profit[i][1]] )
	
	ratioAdjust=sorted(ratioAdjust, key=lambda ele: (-ele[3],-ele[2]))
	#print (ratioAdjust)
	for node in ratioAdjust:
		if ( B-node[1]>=0 ):
			if (node[2]<0):
				print ("error!")
			B=B-node[1]
			totalScore=totalScore+node[2]
			# (inf, inf/cost, cost, score, expect，node id)
			check.append(  [node[4], float(node[4])/node[1], node[1], node[2], inf_profit[node[0]][2], node[0]  ] )
		if (B==0):
			break

	realtime=time.time()-start
	print ("FCMWSGreedy: current divergence:"+str(budget-totalScore)+", D-Ratio:"+str(float(budget-totalScore)/budget)+", time cost (s):"+str(realtime))


	for inf in inf_profit:
		inf.append(0)

	seed=set()
	for c in check:
		inf_profit[c[-1]][-1]=c[2]
		if (c[-1] in seed):
			raise Exception ("duplicate candidate")

		seed.add(c[-1])


	filename=args.output+args.degree.split("/")[-1]+"/FCMWSGreedy/"+"load_"+str(args.load)+"_br_"+str(args.budgetRatio)+"_dis_"+str(args.dis)

	os.makedirs(os.path.dirname(filename), exist_ok=True)
	with open(filename, "w") as f:
		count=0
		while(count<4):
			for inf in inf_profit:			
				
				if (count==3):
					f.write(str(inf[-1])+" ")
				else:
					f.write(str(inf[count])+" ")
			f.write("\n")
			count=count+1		
		f.write(str(realtime))


	return check  


