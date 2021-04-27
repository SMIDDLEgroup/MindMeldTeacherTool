# -*- coding: utf-8 -*-
"""This module contains a template MindMeld app configuration"""

# The namespace of the application. Used to prevent collisions in supporting services across
# applications. If not set here, the app's enclosing directory name is used.
# APP_NAMESPACE = 'app-name'

# Dictionaries for the various NLP classifier configurations

# An example decision tree model for intent classification

INTENT_CLASSIFIER_CONFIG = {
    'model_type': 'text',
    'model_settings': {
        'classifier_type': 'rforest'
    },
    'param_selection': {
        'type': 'k-fold',
        'k': 10,
        'grid': {
            'max_features': ['log2', 'sqrt', 0.01, 0.1]
        },
    },
    "features": {
        'enable-stemming': False,
        "exact": {"scaling": 10},
        'freq': {'bins': 5},
        'char-ngrams': {'lengths': [1, 2, 3]}
    }
}

LANGUAGE_CONFIG = {
    'language': 'uk'
}

ENTITY_RECOGNIZER_CONFIG = {
  'model_type': 'tagger',

  'features': {
    'bag-of-words-seq': {
      'ngram_lengths_to_start_positions': {
         1: [-2, -1, 0, 1, 2],
         2: [-2, -1, 0, 1]
      }
    },
    'in-gaz-span-seq': {},
    'sys-candidates-seq': {
      'start_positions': [-1, 0, 1]
    },
  },
  'model_settings': {
    'classifier_type': 'memm',
    'feature_scaler': 'max-abs',
    'tag_scheme': 'IOB'
  },
  'param_selection': {
    'grid': {
      'C': [0.01, 1, 100, 10000, 1000000, 100000000],
      'penalty': ['l1', 'l2']
    },
   'k': 5,
   'scoring': 'accuracy',
   'type': 'k-fold'
  },
  'params': None,
}

ROLE_CLASSIFIER_CONFIG = {
    'model_type': 'text',
    'model_settings': {'classifier_type': 'rforest'},
    'params': {
        # 'C': 10,
        # 'penalty': 'l2'
    },
    'features': {
        'bag-of-words-before': {
            'ngram_lengths_to_start_positions': {
                1: [-2, -1],
                2: [-2, -1]
            }
        },
        'bag-of-words-after': {
            'ngram_lengths_to_start_positions': {
                1: [0, 1],
                2: [0, 1]
            }
        },
        'entity-length': {},
        'colon-feature': {}
    }
}


"""
# Fill in the other model configurations if necessary
# DOMAIN_CLASSIFIER_CONFIG = {}
# ENTITY_RECOGNIZER_CONFIG = {}
# ROLE_CLASSIFIER_CONFIG = {}
"""

# A example configuration for the parser
"""
# *** Note: these are place holder entity types ***
PARSER_CONFIG = {
    'grandparent': {
        'parent': {},
        'child': {'max_instances': 1}
    },
    'parent': {
        'child': {'max_instances': 1}
    }
}
"""
