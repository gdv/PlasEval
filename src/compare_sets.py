
import itertools
from collections import defaultdict

from math import factorial

import logging

import time
import sys

logger = logging.getLogger(__name__)

def generate_matchings(m, n):
	'''
	Input: Number of copies of a contig in left and right plasmid sets
	Yields: Matchings, each a pair of lists of indices (int) of the contig copies, one for each side.
	'''
	if m >= n:
		fixed = list(range(n))
		for pmutn in itertools.permutations(range(m), n):
			yield (list(pmutn), fixed)
	else:
		fixed = list(range(m))
		for pmutn in itertools.permutations(range(n), m):
			yield (fixed, list(pmutn))

def get_matching_positions(ctg_copies, matching):
	'''
	Input:
		Dictionary of contig copies: L_copies: list of contig copies in left plasmid
									 R_copies: list of contig copies in right plasmid
									 Each copy is a triple [contig, plasmid index (int), position in plasmid (int)]
		Matching: Pair of lists of indices (int) of the contig copies, one for each side
	Returns: Pair of lists of contig copies, one for each side, according to respective indices in the matching 
	'''	
	L, R = ctg_copies['L_copies'], ctg_copies['R_copies']
	l_posn, r_posn = [], []
	for x in matching[0]:
		l_posn.append(L[x])
	for x in matching[1]:
		r_posn.append(R[x])	
	return l_posn, r_posn

def rename_by_matching(matching_dict, contigs_dict):
	'''
	Input: 
		Dictionary of matchings: Key: contig, 
								 Value: matching for copies of contig
								 Each matching is pair of lists of indices (int) of the contig copies, one for each side
		contigs_dict: Key: contig (str), Value: Nested dictionary with 'length' (int)
	Returns:
	 	Two lists of contig copies, one for each plasmid set, renamed with indices according to the input matching 
		Each contig is a triple [contig, plasmid index (int), position in plasmid (int)]
		ctg_len: dict mapping each renamed contig to its length (avoids split('_') in get_partition_cost)
	'''
	reached_contigs = matching_dict.keys()
	left_copies_renamed, right_copies_renamed = [], []
	ctg_len = {}
	for contig in reached_contigs:
		M = matching_dict[contig]
		left_ctgs = M[0]
		right_ctgs = M[1]
		ctg_length = contigs_dict[contig]['length']
		for i in range(len(M[0])):
			renamed = contig+'_'+str(i)
			ctg_len[renamed] = ctg_length
			lpls, lidx = left_ctgs[i][1], left_ctgs[i][2]
			left_copies_renamed.append([renamed, lpls, lidx])
			rpls, ridx = right_ctgs[i][1], right_ctgs[i][2]
			right_copies_renamed.append([renamed, rpls, ridx])
	return left_copies_renamed, right_copies_renamed, ctg_len

def modify_partitions(partitions, common):
	'''
	Input:
		partitions: List of sets of contigs
		common: Set of contigs common to both plasmids 	
	Returns:
		list of partitions, modified by splitting each partition if required, according to the set of common contigs
	'''
	modified_partitions = []
	for S in partitions:
		if len(S.intersection(common)) != 0 or S.intersection(common) != S:
			modified_partitions.append(S.intersection(common))
			modified_partitions.append(S.difference(common))
		elif S.intersection(common) == S:
			modified_partitions.append(S)	
	return modified_partitions		

def get_partition_cost(partitions, ctg_len, p):
	'''
	Input:
		partitions: List of sets of contigs (renamed, e.g. "C1_0")
		ctg_len: dict mapping renamed contig name to its length (int)
		p: exponent for cost computation
	Returns:
		Total of (length of contig sets)^p and the cost of partitioning
	'''	
	total_len = 0
	largest_part_cost = 0
	for S in partitions:
		S_len = 0
		for contig in S:
			S_len += ctg_len[contig]
		if S_len != 0:
			S_cost = S_len**p
			total_len += S_cost
			largest_part_cost = max(largest_part_cost, S_cost)
	cost = total_len - largest_part_cost
	return total_len, cost

def compute_splits_cost(pls_ids, adj, side_ctgs_set_by_pls, opp_ctgs_set_by_pls, ctg_len, p):
	'''
	Input:
		pls_ids: List of plasmid ids,
		adj: adjacency dict (plasmid -> set of neighboring plasmids)
		side_ctgs_set_by_pls: precomputed dict plasmid -> set of contig copies on the side
		opp_ctgs_set_by_pls: precomputed dict plasmid -> set of contig copies on the opposite side
		ctg_len: dict mapping renamed contig name to its length
		p: exponent for cost computation
	Returns:
		Total cost of splits (cuts OR joins) for one plasmid set
	'''
	side_cost = 0
	for node in pls_ids:
		partitions = [side_ctgs_set_by_pls[node]]
		for neighbor in adj.get(node, set()):
			common = side_ctgs_set_by_pls[node].intersection(opp_ctgs_set_by_pls[neighbor])
			partitions = modify_partitions(partitions, common)
		_, cost = get_partition_cost(partitions, ctg_len, p)
		side_cost += cost
	return side_cost

def compute_match_cost(left_contig_copies, right_contig_copies, pls_ids_dict, ctg_len, p):
	'''
	Input:
		List of contig copies, one for each side
		Dictionaries of plasmids and contigs
	Returns:
		Cost of cuts (left side splits) and joins (right side splits)
	'''
	adj = defaultdict(set)
	left_pls_set = set()
	right_pls_set = set()
	for x in left_contig_copies:
		left_pls_set.add(pls_ids_dict['L'].inv[x[1]])
	for x in right_contig_copies:
		right_pls_set.add(pls_ids_dict['R'].inv[x[1]])
	ctg_to_left_pls = defaultdict(set)
	for ctg in left_contig_copies:
		ctg_to_left_pls[ctg[0]].add(pls_ids_dict['L'].inv[ctg[1]])
	ctg_to_right_pls = defaultdict(set)
	for ctg in right_contig_copies:
		ctg_to_right_pls[ctg[0]].add(pls_ids_dict['R'].inv[ctg[1]])
	for ctg_id in ctg_to_left_pls:
		if ctg_id in ctg_to_right_pls:
			for l_pls in ctg_to_left_pls[ctg_id]:
				for r_pls in ctg_to_right_pls[ctg_id]:
					adj[l_pls].add(r_pls)
					adj[r_pls].add(l_pls)
	all_nodes = left_pls_set | right_pls_set
	visited = set()
	components = []
	for start in all_nodes:
		if start not in visited:
			stack = [start]
			comp = set()
			while stack:
				v = stack.pop()
				if v not in visited:
					visited.add(v)
					comp.add(v)
					stack.extend(adj.get(v, set()) - visited)
			components.append(comp)
	left_splits_cost, right_splits_cost = 0, 0
	left_ctgs_set_by_pls = defaultdict(set)
	for x in left_contig_copies:
		left_ctgs_set_by_pls[pls_ids_dict['L'].inv[x[1]]].add(x[0])
	right_ctgs_set_by_pls = defaultdict(set)
	for x in right_contig_copies:
		right_ctgs_set_by_pls[pls_ids_dict['R'].inv[x[1]]].add(x[0])
	for comp in components:
		left_pls_ids = comp & left_pls_set
		right_pls_ids = comp & right_pls_set
		left_splits_cost += compute_splits_cost(left_pls_ids, adj, left_ctgs_set_by_pls, right_ctgs_set_by_pls, ctg_len, p)
		right_splits_cost += compute_splits_cost(right_pls_ids, adj, right_ctgs_set_by_pls, left_ctgs_set_by_pls, ctg_len, p)
	return left_splits_cost, right_splits_cost


def compute_current_cost(matching_dict, pls_ids_dict, contigs_dict, p):
	'''
	Input:
		Dictionary of matchings: Key: contig, Value: matching for copies of contig,
		Dictionary of plasmids: Keys: side (L/R), Values: Bidict of plasmid indices <-> names/ids
		Dictionary of contigs: Key: contig (str), Value: Nested dictionary: length (int), 
																			L_copies/R_copies (list of contig copies in plasmid set)
	Returns:
		Cost of current matching
	'''	
	left_contig_copies, right_contig_copies, ctg_len = rename_by_matching(matching_dict, contigs_dict)
	left_ctg_ids, right_ctg_ids = set(), set()
	for x in left_contig_copies:
		left_ctg_ids.add(x[0])
	for x in right_contig_copies:
		right_ctg_ids.add(x[0])
	return compute_match_cost(left_contig_copies, right_contig_copies, pls_ids_dict, ctg_len, p)

def run_compare_plasmids(contigs_dict, pls_ids_dict, p, max_calls, results_file):
	'''
	Input:
		Dictionary of contigs: 
			Key: contig (str), Value: Nested dictionary:length (int), 
														L_copies: list of contig copies in left plasmid set
														R_copies: list of contig copies in right plasmid set
														Each copy is a triple [contig, plasmid index (int), position in plasmid (int)]
		Dictionary of plasmids, 
			Keys: L, R, Values: Bidict of plasmid indices <-> names/ids
	Returns:
		Dissimilarity score and associated costs (cuts, joins, contig copies present on only left or right plasmid sets)
	'''
	#Computing set of common contigs 
	left_ctg_ids = set([ctg for ctg in contigs_dict.keys() if len(contigs_dict[ctg]['L_copies']) >= 1])
	right_ctg_ids = set([ctg for ctg in contigs_dict.keys() if len(contigs_dict[ctg]['R_copies']) >= 1])
	common_contigs = left_ctg_ids.intersection(right_ctg_ids)

	#Computing upperbound on number of matchings and final_cost
	max_cost = 0
	n_matchings = {}
	max_n_matchings = 1
	for contig in common_contigs:
		m = len(contigs_dict[contig]['L_copies'])
		n = len(contigs_dict[contig]['R_copies'])
		max_cost += m * contigs_dict[contig]['length']
		max_cost += n * contigs_dict[contig]['length']	
		n_matchings[contig] = int(factorial(n)/factorial(n-m)) if n > m else int(factorial(m)/factorial(m-n))
		max_n_matchings *= n_matchings[contig]
	logger.info(f'Maximum possible matchings: {max_n_matchings}')

	start_time = time.time()
	### Branch-N-Bound ###
	current_state = {'level': 0, 'total_cost': 0, 'matching': {}, 'cuts_cost': 0, 'joins_cost': 0, 'unmatched': {}}


	contig_list = list(common_contigs)
	sorted_contig_list = sorted(contig_list, key=lambda ctg: n_matchings[ctg])

	precomputed_matchings = {}
	for contig in common_contigs:
		m = len(contigs_dict[contig]['L_copies'])
		n = len(contigs_dict[contig]['R_copies'])
		precomputed_matchings[contig] = list(generate_matchings(m, n))

	# Greedy initial solution
	greedy_matching = {}
	best_cost = 0
	best_cuts = best_joins = 0
	for contig in sorted_contig_list:
		best_matching = None
		best_cost = float('inf')
		for matching in precomputed_matchings[contig]:
			matched_posns = get_matching_positions(contigs_dict[contig], matching)
			greedy_matching[contig] = matched_posns
			cuts, joins = compute_current_cost(greedy_matching, pls_ids_dict, contigs_dict, p)
			total = cuts + joins
			if total < best_cost:
				best_cost = total
				best_matching = matched_posns
				best_cuts, best_joins = cuts, joins
			del greedy_matching[contig]
		greedy_matching[contig] = best_matching
	logger.info(f'Greedy initial bound: {best_cost}')
	final_state = {'total_cost': best_cost, 'matching': greedy_matching, 'cuts_cost': best_cuts, 'joins_cost': best_joins, 'unmatched': {}}

	count = [0]

	def recursive_compare(current_state, sorted_contig_list, pls_ids_dict, contigs_dict, count):
		'''
		Input:
			Current state dictionary: 
				level: Distance from root of tree (int)
				total_cost: Cost of cuts and joins upto this level (int)
				matching: Nested dictionary with contig ids (str) as keys and a pair (set) of lists of contigs as values
				cuts_cost, joins_cost: Cost of cuts, joins (respectively) upto this level (int)		
				unmatched: Nested dictionary with contigs ids (str) as keys and as values, a dictionary with bin ids as keys and number of extra contigs as values 		
		Updates:
			Current state dictionary
			Final state dictionary (non local variable)
		'''
		nonlocal final_state
		if current_state['total_cost'] >= final_state['total_cost']:
			return
		if current_state['level'] < len(sorted_contig_list):				#Compute cost upto current level
			current_contig = sorted_contig_list[current_state['level']]		#Retrieve contig for current level				
			matchings = precomputed_matchings[current_contig]
			parent_cost = current_state['total_cost']
			for matching in matchings:
				if parent_cost >= final_state['total_cost']:
					break
				matched_posns = get_matching_positions(contigs_dict[current_contig], matching)
				current_state['matching'][current_contig] = matched_posns
				count[0] += 1

				if count[0] > max_calls:
					logger.info(f'Max number of iterations reached: {max_calls}'); sys.exit(f'Max number of iterations reached: {max_calls}')
				current_state['cuts_cost'], current_state['joins_cost'] \
					= compute_current_cost(current_state['matching'], pls_ids_dict, contigs_dict, p)
				current_state['total_cost'] = current_state['cuts_cost'] + current_state['joins_cost']
				if current_state['total_cost'] < final_state['total_cost']:	
					current_state['level'] += 1 
					recursive_compare(current_state, sorted_contig_list, pls_ids_dict, contigs_dict, count)
					current_state['level'] -= 1
				del current_state['matching'][current_contig]

		else:
			final_state['total_cost'] = current_state['total_cost']
			final_state['cuts_cost'], final_state['joins_cost'] = current_state['cuts_cost'], current_state['joins_cost']
			final_state['matching'] = {k: (list(v[0]), list(v[1])) for k, v in current_state['matching'].items()}
	recursive_compare(current_state, sorted_contig_list, pls_ids_dict, contigs_dict, count)
	
	end_time = time.time()
	logger.info(f'Time taken: {end_time - start_time}')
	logger.info(f'Number of function calls: {count[0]}')	
	
	total_len, total_denom, unique_left_cost, unique_right_cost = 0, 0, 0, 0
	for c in contigs_dict:
		#if c not in common_contigs:
		l_copies, r_copies = len(contigs_dict[c]['L_copies']), len(contigs_dict[c]['R_copies'])
		ctg_len = contigs_dict[c]['length']
		unique_left_cost += max(l_copies - r_copies, 0) * (ctg_len**p)
		unique_right_cost += max(r_copies - l_copies, 0) * (ctg_len**p)
		total_len += (l_copies + r_copies) * ctg_len
		total_denom += (l_copies + r_copies) * (ctg_len**p)
 


	dissimilarity_score = (unique_left_cost + unique_right_cost + final_state['total_cost'])
	logger.info(f'contig\tleft_plasmid_id\tleft_plasmid_position\tright_plasmid_id\tright_plasmid_position')
	for ctg in final_state["matching"]:
		n_copies = len(final_state["matching"][ctg][0])
		for i in range(n_copies):
			logger.info(f'{ctg}\t{final_state["matching"][ctg][0][i][1]}\t{final_state["matching"][ctg][0][i][2]}\t{final_state["matching"][ctg][1][i][1]}\t{final_state["matching"][ctg][1][i][2]}')
            
	if total_denom == 0.0: total_denom = 1.0
	results_file.write("Total_ctg_length\t" + str(total_len) + "\n")
	results_file.write("Total_ctg_length_alpha\t" + str(total_denom) + "\n")
	results_file.write("Cuts\t" + str(final_state['cuts_cost']) + "\t" + str(final_state['cuts_cost']/total_denom) + "\n")
	results_file.write("Joins\t" + str(final_state['joins_cost']) + "\t" + str(final_state['joins_cost']/total_denom) + "\n")
	results_file.write("Extra_ctgs\t" + str(unique_left_cost) + "\t" + str(unique_left_cost/total_denom) + "\n")
	results_file.write("Missing_ctgs\t" + str(unique_right_cost) + "\t" + str(unique_right_cost/total_denom) + "\n")
	results_file.write("Dissimilarity\t" + str(dissimilarity_score) + "\t" + str(dissimilarity_score/total_denom) + "\n")
