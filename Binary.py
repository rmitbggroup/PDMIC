import MPD
import copy
import time
import os
def BCDP(W, org_inf_profit,args):

	inf_profit=copy.deepcopy(org_inf_profit)

	start=time.time()
	n=len(inf_profit)
	K = [[0 for y in range(W + 1)] for x in range(n + 1)]
 
	# Build table K[][] in bottom up manner
	for i in range(n + 1):
		for w in range(W + 1):
			if i == 0 or w == 0:
				K[i][w] = 0
			elif inf_profit[i-1][1] <= w:
				price=inf_profit[i-1][1]
				K[i][w] = max(MPD.f(price,inf_profit[i-1][2])
						  + K[i-1][w-price], 
							  K[i-1][w])
			else:
				K[i][w] = K[i-1][w]

	


	for inf in inf_profit:
		inf.append(0)

	ind=n
	weight=W
	while(ind>0):
		if (K[ind][weight] != K[ind - 1][weight]):
			price=inf_profit[ind-1][1]
			weight=weight-price
			inf_profit[ind-1][-1]=price
		
		ind=ind-1

	realtime=time.time()-start



	print ("BCDP: divergence:"+str(W-K[n][W])+",D-ratio:"+str(float(W-K[n][W])/W)+", time cost (s):"+str(realtime))

	inf_profit=sorted( inf_profit, key=lambda ele: (-ele[1]) )
	filename=args.output+args.degree.split("/")[-1]+"/BCDP/"+"load_"+str(args.load)+"_br_"+str(args.budgetRatio)+"_dis_"+str(args.dis)


	if (args.infmax==1):
		filename=args.output+args.degree.split("/")[-1]+"/BCDP/"+"load_"+str(args.load)+"_br_"+str(args.budgetRatio)+"_dis_"+str(args.dis)+"_inf"

	os.makedirs(os.path.dirname(filename), exist_ok=True)
	with open(filename, "w") as f:
		count=0
		while(count<4):
			for inf in inf_profit:
				f.write(str(inf[count])+" ")
			f.write("\n")
			count=count+1	 
		f.write(str(realtime))

	return K[n][W]	



def BCGreedy(B, org_inf_profit,args):


	inf_profit=copy.deepcopy(org_inf_profit)

	start=time.time()
	ratios=[]

	for i in range(len(inf_profit)):
		ratios.append( [i, float(MPD.f(inf_profit[i][1],inf_profit[i][2]))/inf_profit[i][1]] )

	start=time.time()
	rank=sorted(ratios, key=lambda ele: ele[1])

	fullScore=0
	allCost=0
	for inf in inf_profit:
		allCost=allCost+inf[1]
		score=MPD.f(inf[1], inf[2])
		fullScore=fullScore+score

	residue=allCost-B
	seed=set()
	f_min=B
	node_min=-1
	totalScore=0
	for i in range(len(rank)):
		score=MPD.f(inf_profit[rank[i][0]][1],inf_profit[rank[i][0]][2])
		#score=scores[rank[i][0]]

		if (inf_profit[rank[i][0]][1]>residue):
			if (score<f_min):
				f_min=score
				node_min=rank[i][0]

		else:
			if ( float(score)/inf_profit[rank[i][0]][1] < float(f_min)/residue):
				seed.add(rank[i][0])
				residue=residue-inf_profit[rank[i][0]][1]
				totalScore=totalScore+score
				if (residue==0):
					break
			else:
				seed.add(node_min)
				totalScore=totalScore+f_min
				residue=0
				break


	if (residue>0):
		seed.add(node_min)
		totalScore=totalScore+f_min
		residue=residue-inf_profit[node_min][1]


	for inf in inf_profit:
		inf.append(0)


	for i in range(len(inf_profit)):
		if (not i in seed):
			inf_profit[i][-1]=inf_profit[i][1]


	divergence=B-fullScore+totalScore
	realtime=time.time()-start
	print ("BCGreedy: divergence:"+str(divergence)+",D-ratio:"+str(float(divergence)/B)+", time cost (s):"+str(realtime))


	inf_profit=sorted( inf_profit, key=lambda ele: (-ele[1]) )
	filename=args.output+args.degree.split("/")[-1]+"/BCGreedy/"+"load_"+str(args.load)+"_br_"+str(args.budgetRatio)+"_dis_"+str(args.dis)

	os.makedirs(os.path.dirname(filename), exist_ok=True)
	with open(filename, "w") as f:
		count=0
		while(count<4):
			for inf in inf_profit:
				f.write(str(inf[count])+" ")
			f.write("\n")
			count=count+1	
		f.write(str(realtime))

	return totalScore
