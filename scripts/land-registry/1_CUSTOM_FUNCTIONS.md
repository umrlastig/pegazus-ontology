# Javascript functions to add in triplestore
These functions have to be add to the triplestore before starting to build the graph (tested with Ontotext Graph DB). 

## Remove accents
```sparql
PREFIX extfn:<http://www.ontotext.com/js#>

INSERT DATA {
    [] <http://www.ontotext.com/js#register> '''

        function replaceAccent(str) {
            var accentMap = {
                'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
                'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
                'à': 'a', 'è': 'e', 'ì': 'i', 'ò': 'o', 'ù': 'u',
                'À': 'A', 'È': 'E', 'Ì': 'I', 'Ò': 'O', 'Ù': 'U',
                'ä': 'a', 'ë': 'e', 'ï': 'i', 'ö': 'o', 'ü': 'u',
                'Ä': 'A', 'Ë': 'E', 'Ï': 'I', 'Ö': 'O', 'Ü': 'U',
                'â': 'a', 'ê': 'e', 'î': 'i', 'ô': 'o', 'û': 'u',
                'Â': 'A', 'Ê': 'E', 'Î': 'I', 'Ô': 'O', 'Û': 'U',
                'ã': 'a', 'õ': 'o', 'ñ': 'n',
                'Ã': 'A', 'Õ': 'O', 'Ñ': 'N',
                'ç': 'c', 'Ç': 'C'
            };

            return str.split('').map(function(char) {
                return accentMap[char] || char;
            }).join('');
        }
    '''
}
```

## Replace common abreviations
```sparql
PREFIX extfn:<http://www.ontotext.com/js#>

INSERT DATA {
    [] <http://www.ontotext.com/js#register> '''

        function replaceSubwords(str) {
            var subwordMap = {
                'p↑re↓': 'pierre', 
                'j↑n↓': 'jean', 
                'b↑te↓': 'baptiste', 
                'bap↑te↓': 'baptiste', 
                'jb↑te↓': 'jean baptiste',
                'f↑ois↓': 'françois', 
                'j↑d↓': 'jean', 
                'v↑e↓': 'veuve', 
                'v↑ve↓': 'veuve', 
                'h↑re↓': 'heritier',
            };

            var pattern = new RegExp(Object.keys(subwordMap).join("|"), "g");

            return str.replace(pattern, function(matched){
                return subwordMap[matched];
            });
        }
    '''
}
```

## [NOT USED] String similarity bigrams
```sparql
PREFIX extfn:<http://www.ontotext.com/js#>

INSERT DATA {
    [] <http://www.ontotext.com/js#register> '''
        function stringSimilarityBigrams(str1, str2) {
            function getBigrams(str) {
                var s = str.toLowerCase();
                var v = new Array(s.length - 1);
                for (var i = 0; i < v.length; i++) {
                    v[i] = s.slice(i, i + 2);
                }
                return v;
            }

            var pairs1 = getBigrams(str1);
            var pairs2 = getBigrams(str2);
            var union = pairs1.length + pairs2.length;
            var hitCount = 0;

            for (var x = 0; x < pairs1.length; x++) {
                for (var y = 0; y < pairs2.length; y++) {
                    if (pairs1[x] === pairs2[y]) {
                        hitCount++;
                    }
                }
            }

            return (2.0 * hitCount) / union;
        }
    '''
}
```
## String similarity using levenshtein
```sparql
PREFIX extfn:<http://www.ontotext.com/js#>

INSERT DATA {
    [] <http://www.ontotext.com/js#register> '''
        function normalizedLevenshtein(str1, str2) {
            function levenshtein(a, b) {
                if (a.length == 0) return b.length;
                if (b.length == 0) return a.length;

                var matrix = [];

                // increment along the first column of each row
                var i;
                for (i = 0; i <= b.length; i++) {
                    matrix[i] = [i];
                }

                // increment each column in the first row
                var j;
                for (j = 0; j <= a.length; j++) {
                    matrix[0][j] = j;
                }

                // fill in the rest of the matrix
                for (i = 1; i <= b.length; i++) {
                    for (j = 1; j <= a.length; j++) {
                        if (b.charAt(i - 1) == a.charAt(j - 1)) {
                            matrix[i][j] = matrix[i - 1][j - 1];
                        } else {
                            matrix[i][j] = Math.min(matrix[i - 1][j - 1] + 1, // substitution
                                                    Math.min(matrix[i][j - 1] + 1, // insertion
                                                             matrix[i - 1][j] + 1)); // deletion
                        }
                    }
                }

                return matrix[b.length][a.length];
            }

            var levDistance = levenshtein(str1, str2);
            var maxLength = Math.max(str1.length, str2.length);
            return (maxLength === 0) ? 1.0 : (1 - (levDistance / maxLength));
        }
    '''
}
```

## Sort a list of values
3 parameters :
- list of value (str)
- order : *asc* or *desc*
- separator
Return the sorted list as a string with the same separator.
```sparql
PREFIX extfn:<http://www.ontotext.com/js#>

INSERT DATA {
    [] <http://www.ontotext.com/js#register> '''
        function sortList(str, order, separator) {
            var list = str.split(separator);
            list.sort(function(a, b) {
                if (order === 'asc') {
                    return a.localeCompare(b);
                } else if (order === 'desc') {
                    return b.localeCompare(a);
                } else {
                    throw new Error("Invalid order parameter. Use 'asc' or 'desc'.");
                }
            });
            return list.join(separator);
        }
    '''
}

```