#!/usr/bin/env python2
# -*- encoding: UTF8 -*-

import re
import rigolFG

testResponses = [ 
  #manufacterer, model, serial number and the edition number
  'RIGOL TECHNOLOGIES,DG1022 ,DG1D135208595,,00.03.00.08.00.02.08',
  'RIGOL TECHNOLOGIES,DG1022 ,DG1D135208559,,00.03.00.08.00.02.08',
  'RIGOL TECHNOLOGIES,DG1022 ,DG1D135208955,,00.03.20.08.00.02.08',
  'RIGOL TECHNOLOGIES,DG1022,DG1D135208955,,00.03.20.08.00.02.08',
  'RIGOL TECHNOLOGIES,DG1022 ,DG1D135208955,00.03.20.08.00.02.08',
]

for response in testResponses:
    try:
        print rigolFG.RigolFunctionGenerator.validate('*IDN?', response)
    except Exception, e:
        print type(e), str(e)
