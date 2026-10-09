import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import xmlschema, xsddiag, cairosvg
s=xmlschema.XMLSchema10(os.path.join(OUT, '..', 'Monolithic', 'idm_monolithic_V2.0.xsd'))
specs={'fig2_idm':('idm',[],None),'fig3_specId':('specId',[],None),'fig4_authoring':('authoring',['author'],None),
 'fig5_uc':('uc',['description','image','classification'],int(sys.argv[1]) if len(sys.argv)>1 else 12),'fig6_bcm':('businessContextMap',['pm','im','tm','diagram'],None),
 'fig7_er':('er',['informationUnit','expression','formalRuleLanguage'],None)}
for k,(r,ex,sp) in specs.items():
    W,H=xsddiag.render(s,r,ex,os.path.join(OUT, f'{k}.svg'),split=sp)
    cairosvg.svg2png(url=os.path.join(OUT, f'{k}.svg'),write_to=os.path.join(OUT, f'{k}.png'),scale=2)
    print(k,round(W),round(H), round(H/W,2))
