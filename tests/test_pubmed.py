#!/usr/bin/env python
# -*- coding: utf-8 -*-
from litter_getter import pubmed

from unittest import TestCase


class TestPubMedSettings(object):

    def test_default(self):
        assert pubmed.settings.tool == 'PLACEHOLDER'
        assert pubmed.settings.email == 'PLACEHOLDER'

    def test_connection(self):
        pubmed.connect('MYTOOl', 'myemail@email.com')
        assert pubmed.settings.tool == 'MYTOOl'
        assert pubmed.settings.email == 'myemail@email.com'


class PubMedSearchTests(TestCase):

    def setUp(self):
        pubmed.connect('MYTOOl', 'myemail@email.com')
        self.term = "science[journal] AND breast cancer AND 2008[pdat]"
        self.results_list = ['19008416', '18927361', '18787170', '18487186', '18239126', '18239125']

    def test_standard_query(self):
        self.search = pubmed.PubMedSearch(term=self.term)
        self.search.get_ids_count()
        self.search.get_ids()
        self.assertEqual(self.search.request_count, 1)
        self._results_check()

    def test_multiquery(self):
        self.search = pubmed.PubMedSearch(term=self.term, retmax=3)
        self.search.get_ids_count()
        self.search.get_ids()
        self.assertEqual(self.search.request_count, 2)
        self._results_check()

    def test_changes_from_previous_search(self):
        self.search = pubmed.PubMedSearch(term=self.term)
        self.search.get_ids_count()
        self.search.get_ids()
        old_ids_list = ['999999', '19008416', '18927361', '18787170', '18487186']
        changes = self.search.get_changes_from_previous_search(old_ids_list=old_ids_list)
        self.assertEqual(changes['added'], set(['18239126', '18239125']))
        self.assertEqual(changes['removed'], set(['999999']))

    def test_complex_query(self):
        """Ensure complicated search term executes and returns results."""
        self.term = """(monomethyl OR MEP OR mono-n-butyl OR MBP OR mono (3-carboxypropyl) OR mcpp OR monobenzyl OR mbzp OR mono-isobutyl OR mibp OR mono (2-ethylhexyl) OR mono (2-ethyl-5-oxohexyl) OR meoph OR mono (2-ethyl-5-carboxypentyl) OR mecpp OR mepp OR mono (2-ethyl-5-hydroxyhexyl) OR mehp OR mono (2-ethyl-5-oxyhexyl) OR mono (2-ethyl-4-hydroxyhexyl) OR mono (2-ethyl-4-oxyhexyl) OR mono (2-carboxymethyl) OR mmhp OR mehp OR dehp OR 2-ethylhexanol OR (phthalic acid)) AND (liver OR hepato* OR hepat*) AND ((cell proliferation) OR (cell growth) OR (dna replication) OR (dna synthesis) OR (replicative dna synthesis) OR mitosis OR (cell division) OR (growth response) OR hyperplasia OR hepatomegaly) AND (mouse OR rat OR hamster OR rodent OR murine OR Mus musculus or Rattus)"""  # noqa
        self.search = pubmed.PubMedSearch(term=self.term)
        self.search.get_ids_count()
        self.search.get_ids()
        self.assertTrue(len(self.search.ids) >= 212)

    def _results_check(self):
        self.assertEqual(self.search.id_count, 6)
        self.assertListEqual(self.search.ids, self.results_list)


class PubMedFetchTests(TestCase):

    def setUp(self):
        pubmed.connect('MYTOOl', 'myemail@email.com')
        self.ids = [
            '19008416', '18927361', '18787170',
            '18487186', '18239126', '18239125'
        ]

    def test_standard_query(self):
        self.fetch = pubmed.PubMedFetch(id_list=self.ids)
        self.fetch.get_content()
        self.assertEqual(self.fetch.request_count, 1)
        self._results_check()

    def test_multiquery(self):
        self.fetch = pubmed.PubMedFetch(id_list=self.ids, retmax=3)
        self.fetch.get_content()
        self.assertEqual(self.fetch.request_count, 2)
        self._results_check()

    def test_utf8(self):
        # these ids have UTF-8 text in the abstract; make sure we can import
        # and the abstract field captures this value.
        self.ids = [23878845, 16080930]
        self.fetch = pubmed.PubMedFetch(id_list=self.ids)
        self.fetch.get_content()
        # assert that a unicode value exists in text
        self.assertTrue(self.fetch.content[0]['abstract'].find(u'\u03b1') > -1)

    def test_collective_author(self):
        # this doesn't have an individual author but rather a collective author
        self.ids = [21860499]
        self.fetch = pubmed.PubMedFetch(id_list=self.ids)
        self.fetch.get_content()
        self.assertEqual(
            self.fetch.content[0]['authors_short'],
            u'National Toxicology Program'
        )

    def test_structured_abstract(self):
        """
        Ensured structured abstract XML is captured.

        Example: https://www.ncbi.nlm.nih.gov/pubmed/21813367/
        """
        self.ids = (21813367, )
        self.fetch = pubmed.PubMedFetch(id_list=self.ids)
        self.fetch.get_content()
        abstract_text = u"""<span class="abstract_label">BACKGROUND: </span>People living or working in eastern Ohio and western West Virginia have been exposed to perfluorooctanoic acid (PFOA) released by DuPont Washington Works facilities.<br><span class="abstract_label">OBJECTIVES: </span>Our objective was to estimate historical PFOA exposures and serum concentrations experienced by 45,276 non-occupationally exposed participants in the C8 Health Project who consented to share their residential histories and a 2005-2006 serum PFOA measurement.<br><span class="abstract_label">METHODS: </span>We estimated annual PFOA exposure rates for each individual based on predicted calibrated water concentrations and predicted air concentrations using an environmental fate and transport model, individual residential histories, and maps of public water supply networks. We coupled individual exposure estimates with a one-compartment absorption, distribution, metabolism, and excretion (ADME) model to estimate time-dependent serum concentrations.<br><span class="abstract_label">RESULTS: </span>For all participants (n = 45,276), predicted and observed median serum concentrations in 2005-2006 are 14.2 and 24.3 ppb, respectively [Spearman's rank correlation coefficient (r(s)) = 0.67]. For participants who provided daily public well water consumption rate and who had the same residence and workplace in one of six municipal water districts for 5 years before the serum sample (n = 1,074), predicted and observed median serum concentrations in 2005-2006 are 32.2 and 40.0 ppb, respectively (r(s) = 0.82).<br><span class="abstract_label">CONCLUSIONS: </span>Serum PFOA concentrations predicted by linked exposure and ADME models correlated well with observed 2005-2006 human serum concentrations for C8 Health Project participants. These individualized retrospective exposure and serum estimates are being used in a variety of epidemiologic studies being conducted in this region."""  # NOQA
        self.maxDiff = None
        self.assertEqual(self.fetch.content[0]['abstract'], abstract_text)

    def test_doi(self):
        """
        Ensure DOI is obtained.

        Ex: https://www.ncbi.nlm.nih.gov/pubmed/21813142?retmod=xml&report=xml&format=text  # NOQA
        """
        self.ids = (21813142, )
        self.fetch = pubmed.PubMedFetch(id_list=self.ids)
        self.fetch.get_content()
        doi = u"10.1016/j.medcli.2011.05.017"
        self.assertEqual(self.fetch.content[0]['doi'], doi)

    def test_book(self):
        self.ids = (26468569, )
        self.fetch = pubmed.PubMedFetch(id_list=self.ids)
        self.fetch.get_content()
        obj = self.fetch.content[0]
        obj.pop('xml')
        obj.pop('abstract')
        expected = {
            'authors_short': u'Committee on Predictive-Toxicology Approaches for Military Assessments of Acute Exposures et al.',
            'doi': '10.17226/21775',
            'year': 2015,
            'PMID': '26468569',
            'title': 'Application of Modern Toxicology Approaches for Predicting Acute Toxicity for Chemical Defense',
            'citation': u'(2015). Washington (DC): National Academies Press (US).',
            'authors_list': [
                'Committee on Predictive-Toxicology Approaches for Military Assessments of Acute Exposures',
                'Committee on Toxicology',
                'Board on Environmental Studies and Toxicology',
                'Board on Life Sciences',
                'Division on Earth and Life Studies',
                'The National Academies of Sciences, Engineering, and Medicine'
            ]
        }
        self.assertEqual(obj, expected)

    def test_book_chapter(self):
        self.ids = (20301382, )
        self.fetch = pubmed.PubMedFetch(id_list=self.ids)
        self.fetch.get_content()
        obj = self.fetch.content[0]
        obj.pop('xml')
        obj.pop('abstract')
        expected = {
            'PMID': '20301382',
            'authors_list': [
                u'DiMauro S',
                u'Hirano M'
            ],
            'authors_short': u'DiMauro S and Hirano M',
            'citation': u'GeneReviews(®) (1993). Seattle (WA): University of Washington, Seattle.',
            'doi': None,
            'title': 'Mitochondrial DNA Deletion Syndromes',
            'year': 1993
        }
        self.assertEqual(obj, expected)

    def _results_check(self):
        self.assertEqual(len(self.fetch.content), 6)
        self.assertListEqual(
            [item['PMID'] for item in self.fetch.content],
            self.ids
        )

        citations = [
            "Science 2008; 322 (5908):1695-9",
            "Science 2008; 322 (5900):357",
            "Science 2008; 321 (5895):1499-502",
            "Science 2008; 320 (5878):903-9",
            "Science 2008; 319 (5863):620-4",
            "Science 2008; 319 (5863):617-20"
        ]
        self.assertListEqual(
            [item['citation'] for item in self.fetch.content],
            citations
        )

        authors_short = [
            "Varambally S et al.",
            "Couzin J",
            "Mao JH et al.",
            "Bromberg KD et al.",
            "Schlabach MR et al.",
            "Silva JM et al."
        ]
        self.assertListEqual(
            [item['authors_short'] for item in self.fetch.content],
            authors_short
        )
