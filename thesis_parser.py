# Thomas Schaffner
#! /usr/bin/python

import argparse
import textract
import re
import os

def parse_pdf(pdf):
	text = textract.process(pdf)
	words = text.split()
	clean_words = [word for word in words if "\\x" not in word]

	return clean_words

def parse_sentences(pdf):
	text = textract.process(pdf)

	reg = "[.?!]"

	sentences = re.split(reg, text)

	return [s for s in sentences if "\\x" not in s]

def calc_max_length(cw):
	return max([len(w) for w in cw])

def calc_average_length(cw):
	return sum([len(w) for w in cw]) / len(cw)


def calc_distribution(cw):
	m = calc_max_length(cw)

	d = []

	for i in xrange(m):
		d.append(0)

	for w in cw:
		d[len(w) - 1] += 1

	return d

def calc_average_wps(cs):
	return sum(len(s.split()) for s in cs) / len(cs)

def calc_max_wps(cs):
	return max(len(s.split()) for s in cs)

def calc_binned_word_counts(cw):
	cc = 0
	sums = [0]
	sums.append(0)
	biniter = 0
	for i in xrange(len(cw)):
		w = cw[i]
		cc += len(w)
		sums[biniter] += 1
		if (cc >= 1000):
			cc = 0
			sums.append(0)
			biniter += 1

	return sums

def format_stats_line(subject, wc, m, a, sm, sa, mwps, awps):
	return subject + "," + str(wc) + "," + str(m) + "," + str(a) + "," + str(sm) + "," + str(sa) + "," + str(mwps) + "," + str(awps) + "\n"

def format_dist_line(subject, dist, sdist, bdist):
	return subject + "," + ",".join([str(d) for d in dist]) + "\n" + "-," + ",".join([str(s) for s in sdist]) + "\n" + "-," + ",".join([str(s) for s in bdist]) + "\n"

def label_stats_file(f):
	f.write("subject,word_count,max_word_length,average_word_length,max_sentence_length,average_sentence_length,max_words_per_sentence,average_words_per_sentence\n")
	f.flush()

def label_dist_file(f):
	f.write("subject,[num_words_size_1,num_words_size_2,...]\n")
	f.write("-,[num_sentences_size_1,num_sentences_size_2,...]\n")
	f.write("-,[num_words_in_first_1000_chars,...]\n")
	f.flush()

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("-i", "--input", help="Input pdf", required=True)
	parser.add_argument("-s", "--stats_output", help="Output file for stats", required=True)
	parser.add_argument("-d", "--dist_output", help="Output file for distribution", required=True)
	parser.add_argument("-j", "--subject", help="Subject department of thesis", required=True)

	options = parser.parse_args()

	run(options)


def run(options):
	clean_words = parse_pdf(options.input)

	max_length = calc_max_length(clean_words)
	average_length = calc_average_length(clean_words)
	distribution = calc_distribution(clean_words)
	binned_words = calc_binned_word_counts(clean_words)

	
	clean_sentences = parse_sentences(options.input)

	max_s_length = calc_max_length(clean_sentences)
	average_s_length = calc_average_length(clean_sentences)
	s_distribution = calc_distribution(clean_sentences)
	average_wps = calc_average_wps(clean_sentences)
	max_wps = calc_max_wps(clean_sentences)

	sfile = open(options.stats_output, 'a')
	if os.stat(options.stats_output).st_size == 0:
		label_stats_file(sfile)
	sfile.write(format_stats_line(options.subject, len(clean_words), max_length, average_length, max_s_length, average_s_length, max_wps, average_wps))
	sfile.flush()

	dfile = open(options.dist_output, 'a')
	if os.stat(options.dist_output).st_size == 0:
		label_dist_file(dfile)
	dfile.write(format_dist_line(options.subject, distribution, s_distribution, binned_words))
	dfile.flush()


if __name__ == "__main__":
	main()
