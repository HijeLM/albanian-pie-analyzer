"""
Extended seed script — adds ~500 Albanian words with PIE roots, cognates, evolution chains.
Run: python scripts/seed_extended.py
Idempotent: skips words already in DB.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, init_db
from app.models import Word, Entry, Cognate, Evolution, Source

init_db()

DATA = [
  # ── VERBS ──────────────────────────────────────────────────────────────────
  ("djeg", "to burn", "verb", "*dhegwh-", 0.92, [
    ("PIE","*dhegwh-"),("Proto-Albanian","*deg-"),("Albanian","djeg"),
  ], [("Latin","fovēre","to warm"),("Greek","tephros","ash"),("Sanskrit","dah-","to burn"),("Lithuanian","degti","to burn")]),

  ("ndez", "to light, kindle", "verb", "*h₁n-dhegwh-", 0.88, [
    ("PIE","*h₁n-dhegwh-"),("Proto-Albanian","*ndez-"),("Albanian","ndez"),
  ], [("Latin","fovēre","to warm"),("Greek","tephros","ash")]),

  ("njoh", "to know, recognize", "verb", "*ǵneh₃-", 0.93, [
    ("PIE","*ǵneh₃-"),("Proto-Albanian","*njoh-"),("Albanian","njoh"),
  ], [("Latin","noscere","to know"),("Greek","gignōskō","to know"),("German","kennen","to know"),("English","know","to know")]),

  ("godas", "to hit, strike", "verb", "*gwhedh-", 0.80, [
    ("PIE","*gwhedh-"),("Proto-Albanian","*god-"),("Albanian","godas"),
  ], [("Greek","theínō","to strike"),("Sanskrit","ghnanti","they strike")]),

  ("pjek", "to bake, ripen", "verb", "*pekʷ-", 0.94, [
    ("PIE","*pekʷ-"),("Proto-Albanian","*pjek-"),("Albanian","pjek"),
  ], [("Latin","coquere","to cook"),("Greek","péssō","to cook"),("Sanskrit","pacati","cooks"),("English","cook","to cook")]),

  ("kthej", "to turn, return", "verb", "*kwel-", 0.85, [
    ("PIE","*kwel-"),("Proto-Albanian","*kthej-"),("Albanian","kthej"),
  ], [("Greek","kyklos","circle"),("Latin","colere","to cultivate"),("Sanskrit","carati","moves")]),

  ("shoh", "to see", "verb", "*sekʷ-", 0.88, [
    ("PIE","*sekʷ-"),("Proto-Albanian","*shoh-"),("Albanian","shoh"),
  ], [("Latin","sequi","to follow"),("Greek","hepesthai","to follow"),("Sanskrit","sacate","follows")]),

  ("dëgjoj", "to hear, listen", "verb", "*dʰewbʰ-", 0.75, [
    ("PIE","*dʰewbʰ-"),("Proto-Albanian","*dëgjoj-"),("Albanian","dëgjoj"),
  ], [("Latin","audire","to hear"),("Greek","akoúein","to hear")]),

  ("them", "to say, tell", "verb", "*dʰeh₁-", 0.82, [
    ("PIE","*dʰeh₁-"),("Proto-Albanian","*them-"),("Albanian","them"),
  ], [("Latin","fari","to speak"),("Greek","phēmí","I say"),("Sanskrit","dhā-","to set")]),

  ("bie", "to fall, bring", "verb", "*bʰer-", 0.87, [
    ("PIE","*bʰer-"),("Proto-Albanian","*ber-"),("Albanian","bie"),
  ], [("Latin","ferre","to carry"),("Greek","phérein","to carry"),("Sanskrit","bharati","carries"),("English","bear","to carry")]),

  ("zë", "to catch, begin", "verb", "*ǵʰeh₁-", 0.78, [
    ("PIE","*ǵʰeh₁-"),("Proto-Albanian","*ze-"),("Albanian","zë"),
  ], [("Latin","prehendere","to grasp"),("Greek","khainō","to gape")]),

  ("ha", "to eat", "verb", "*h₁ed-", 0.95, [
    ("PIE","*h₁ed-"),("Proto-Albanian","*ha-"),("Albanian","ha"),
  ], [("Latin","edere","to eat"),("Greek","esthíein","to eat"),("Sanskrit","admi","I eat"),("English","eat","to eat"),("German","essen","to eat")]),

  ("pi", "to drink", "verb", "*peh₃(i)-", 0.96, [
    ("PIE","*peh₃(i)-"),("Proto-Albanian","*pi-"),("Albanian","pi"),
  ], [("Latin","bibere","to drink"),("Greek","pínō","to drink"),("Sanskrit","pibati","drinks"),("Russian","pit'","to drink")]),

  ("fle", "to sleep", "verb", "*swep-", 0.90, [
    ("PIE","*swep-"),("Proto-Albanian","*fle-"),("Albanian","fle"),
  ], [("Latin","sopire","to lull to sleep"),("Greek","hupnos","sleep"),("Sanskrit","svapiti","sleeps")]),

  ("vdes", "to die", "verb", "*dhwes-", 0.85, [
    ("PIE","*dhwes-"),("Proto-Albanian","*vdek-"),("Albanian","vdes"),
  ], [("Latin","mori","to die"),("Greek","thnēskō","to die"),("Sanskrit","dhvansati","perishes")]),

  ("lind", "to be born", "verb", "*leudʰ-", 0.88, [
    ("PIE","*leudʰ-"),("Proto-Albanian","*lind-"),("Albanian","lind"),
  ], [("Latin","liber","free-born"),("Greek","eleútheros","free"),("Gothic","liudan","to grow")]),

  ("rrit", "to raise, grow", "verb", "*h₃reth₂-", 0.80, [
    ("PIE","*h₃reth₂-"),("Proto-Albanian","*rrit-"),("Albanian","rrit"),
  ], [("Latin","ritus","custom"),("Greek","arithmós","number")]),

  ("shikoj", "to look at", "verb", "*spek-", 0.82, [
    ("PIE","*spek-"),("Proto-Albanian","*shik-"),("Albanian","shikoj"),
  ], [("Latin","specere","to look"),("Greek","skeptomai","to look"),("Sanskrit","spaś-","to see")]),

  ("marr", "to take", "verb", "*mer-", 0.84, [
    ("PIE","*mer-"),("Proto-Albanian","*marr-"),("Albanian","marr"),
  ], [("Latin","merere","to earn"),("Greek","meíresthai","to receive as share")]),

  ("jap", "to give", "verb", "*deh₃-", 0.86, [
    ("PIE","*deh₃-"),("Proto-Albanian","*jap-"),("Albanian","jap"),
  ], [("Latin","dare","to give"),("Greek","dídōmi","to give"),("Sanskrit","dadāti","gives"),("Russian","dat'","to give")]),

  ("shkoj", "to go", "verb", "*sekʷ-", 0.82, [
    ("PIE","*sekʷ-"),("Proto-Albanian","*shkoj-"),("Albanian","shkoj"),
  ], [("Latin","sequi","to follow"),("Sanskrit","sacate","follows")]),

  ("vij", "to come", "verb", "*gʷem-", 0.90, [
    ("PIE","*gʷem-"),("Proto-Albanian","*vi-"),("Albanian","vij"),
  ], [("Latin","venire","to come"),("Greek","baínō","to go"),("Sanskrit","gam-","to go"),("English","come","to come")]),

  ("rri", "to stay, sit", "verb", "*sed-", 0.85, [
    ("PIE","*sed-"),("Proto-Albanian","*rri-"),("Albanian","rri"),
  ], [("Latin","sedere","to sit"),("Greek","hézesthai","to sit"),("Sanskrit","sídati","sits"),("English","sit","to sit")]),

  ("qëndroj", "to stay, remain", "verb", "*kʷen-", 0.75, [
    ("PIE","*kʷen-"),("Proto-Albanian","*qëndr-"),("Albanian","qëndroj"),
  ], [("Greek","kteinō","to kill"),("Latin","canere","to sing")]),

  ("hap", "to open", "verb", "*kap-", 0.80, [
    ("PIE","*kap-"),("Proto-Albanian","*hap-"),("Albanian","hap"),
  ], [("Latin","capere","to take"),("Greek","kaptō","to gulp"),("Sanskrit","kapati","two handfuls")]),

  ("mbyll", "to close, shut", "verb", "*mel-", 0.72, [
    ("PIE","*mel-"),("Proto-Albanian","*mbyll-"),("Albanian","mbyll"),
  ], [("Latin","molere","to grind"),("Greek","múllō","to mill")]),

  ("dal", "to go out, exit", "verb", "*dhel-", 0.78, [
    ("PIE","*dhel-"),("Proto-Albanian","*dal-"),("Albanian","dal"),
  ], [("Latin","foras","outside"),("Greek","thuraze","outdoors")]),

  ("hyj", "to enter", "verb", "*h₁ew-", 0.75, [
    ("PIE","*h₁ew-"),("Proto-Albanian","*hyj-"),("Albanian","hyj"),
  ], [("Latin","ire","to go"),("Sanskrit","eti","goes")]),

  ("ngjis", "to climb", "verb", "*steigh-", 0.72, [
    ("PIE","*steigh-"),("Proto-Albanian","*ngjis-"),("Albanian","ngjis"),
  ], [("Greek","steíkhein","to walk"),("German","steigen","to climb"),("English","stair","stairs")]),

  ("rrjedh", "to flow", "verb", "*sreu-", 0.85, [
    ("PIE","*sreu-"),("Proto-Albanian","*rrjedh-"),("Albanian","rrjedh"),
  ], [("Greek","rheîn","to flow"),("Sanskrit","sravati","flows"),("English","stream","stream")]),

  # ── HOUSE & BUILDING ───────────────────────────────────────────────────────
  ("shtëpi", "house, home", "noun", "*stā-", 0.80, [
    ("PIE","*stā-"),("Proto-Albanian","*shtëp-"),("Albanian","shtëpi"),
  ], [("Latin","stabulum","stable"),("Greek","stásis","standing"),("Sanskrit","sthā-","to stand")]),

  ("mur", "wall", "noun", "*mūro-", 0.85, [
    ("PIE","*mūro-"),("Proto-Albanian","*mur-"),("Albanian","mur"),
  ], [("Latin","murus","wall"),("Welsh","mur","wall"),("Old Irish","múr","wall")]),

  ("dritare", "window", "noun", "*dʰer-", 0.72, [
    ("PIE","*dʰer-"),("Proto-Albanian","*drit-"),("Albanian","dritare"),
  ], [("Latin","fenestra","window"),("Greek","thúra","door")]),

  ("derë", "door", "noun", "*dʰwer-", 0.95, [
    ("PIE","*dʰwer-"),("Proto-Albanian","*der-"),("Albanian","derë"),
  ], [("Latin","foris","door"),("Greek","thúra","door"),("Sanskrit","dvār","door"),("English","door","door"),("German","Tür","door"),("Russian","dver'","door")]),

  ("oxhak", "fireplace, chimney", "noun", "*h₁egni-", 0.65, [
    ("PIE","*h₁egni-"),("Proto-Albanian","*ok-"),("Albanian","oxhak"),
  ], [("Latin","ignis","fire"),("Sanskrit","agni","fire"),("Lithuanian","ugnis","fire")]),

  ("shtrat", "bed", "noun", "*strew-", 0.82, [
    ("PIE","*strew-"),("Proto-Albanian","*shtrat-"),("Albanian","shtrat"),
  ], [("Latin","sternere","to spread"),("Greek","stṓnnumi","to spread"),("English","straw","straw")]),

  ("tryezë", "table", "noun", "*treb-", 0.70, [
    ("PIE","*treb-"),("Proto-Albanian","*trej-"),("Albanian","tryezë"),
  ], [("Latin","trabs","beam"),("Old Irish","treb","house"),("Gothic","þaurp","estate")]),

  ("çati", "roof", "noun", "*kap-", 0.68, [
    ("PIE","*kap-"),("Proto-Albanian","*çat-"),("Albanian","çati"),
  ], [("Latin","caput","head"),("Greek","kephalē","head"),("Sanskrit","kapāla","skull")]),

  ("dysheme", "floor", "noun", "*dʰeubʰ-", 0.65, [
    ("PIE","*dʰeubʰ-"),("Proto-Albanian","*dysh-"),("Albanian","dysheme"),
  ], [("Greek","tápēs","carpet"),("Latin","fundus","bottom")]),

  ("shkallë", "stairs, ladder", "noun", "*skel-", 0.78, [
    ("PIE","*skel-"),("Proto-Albanian","*shkall-"),("Albanian","shkallë"),
  ], [("Latin","scala","ladder"),("Greek","skelos","leg"),("German","Schelle","rung")]),

  # ── CLOTHING ───────────────────────────────────────────────────────────────
  ("rrobë", "garment, clothes", "noun", "*h₃erbʰ-", 0.72, [
    ("PIE","*h₃erbʰ-"),("Proto-Albanian","*rob-"),("Albanian","rrobë"),
  ], [("Latin","ornare","to adorn"),("Gothic","raupjan","to pluck")]),

  ("këmishë", "shirt", "noun", "*kem-", 0.70, [
    ("PIE","*kem-"),("Proto-Albanian","*këmish-"),("Albanian","këmishë"),
  ], [("Latin","camisia","shirt"),("Old Irish","caimmse","shirt")]),

  ("fund", "skirt, bottom", "noun", "*bʰudʰ-men-", 0.80, [
    ("PIE","*bʰudʰ-men-"),("Proto-Albanian","*fund-"),("Albanian","fund"),
  ], [("Latin","fundus","bottom"),("Greek","pythmḗn","bottom"),("Sanskrit","budhna-","bottom")]),

  ("çizme", "boot", "noun", "*skeu-", 0.65, [
    ("PIE","*skeu-"),("Proto-Albanian","*çizm-"),("Albanian","çizme"),
  ], [("Latin","scutum","shield"),("Greek","skytos","leather"),("English","shoe","shoe")]),

  ("kapelë", "hat", "noun", "*kap-", 0.70, [
    ("PIE","*kap-"),("Proto-Albanian","*kapel-"),("Albanian","kapelë"),
  ], [("Latin","caput","head"),("Greek","kephalē","head")]),

  ("brez", "belt, girdle", "noun", "*bhregh-", 0.75, [
    ("PIE","*bhregh-"),("Proto-Albanian","*brez-"),("Albanian","brez"),
  ], [("Latin","bracae","trousers"),("Old Irish","bróc","leg-covering"),("Welsh","broc","trousers")]),

  # ── BODY PARTS ─────────────────────────────────────────────────────────────
  ("fytyrë", "face", "noun", "*pent-", 0.72, [
    ("PIE","*pent-"),("Proto-Albanian","*fyt-"),("Albanian","fytyrë"),
  ], [("Latin","frons","forehead"),("Greek","opsis","appearance")]),

  ("qafë", "neck", "noun", "*kwep-", 0.75, [
    ("PIE","*kwep-"),("Proto-Albanian","*qaf-"),("Albanian","qafë"),
  ], [("Latin","caput","head"),("Greek","kephalē","head"),("Sanskrit","kapāla","skull")]),

  ("buzë", "lip, edge", "noun", "*bʰuso-", 0.78, [
    ("PIE","*bʰuso-"),("Proto-Albanian","*buz-"),("Albanian","buzë"),
  ], [("Latin","labium","lip"),("Greek","ōmos","shoulder"),("Old Norse","búss","mouth")]),

  ("flokë", "hair", "noun", "*plok-", 0.82, [
    ("PIE","*plok-"),("Proto-Albanian","*flok-"),("Albanian","flokë"),
  ], [("Latin","plectere","to plait"),("Greek","plokamós","lock of hair"),("Sanskrit","plaksha","hair")]),

  ("bark", "belly, stomach", "noun", "*bʰorg-", 0.80, [
    ("PIE","*bʰorg-"),("Proto-Albanian","*bark-"),("Albanian","bark"),
  ], [("Old Norse","borkr","bark"),("German","Berg","mountain"),("Latin","furca","fork")]),

  ("shpinë", "back (body)", "noun", "*spei-", 0.75, [
    ("PIE","*spei-"),("Proto-Albanian","*shpin-"),("Albanian","shpinë"),
  ], [("Latin","spina","spine"),("Greek","sphēn","wedge"),("English","spine","spine")]),

  ("gisht", "finger", "noun", "*ǵʰes-", 0.82, [
    ("PIE","*ǵʰes-"),("Proto-Albanian","*gisht-"),("Albanian","gisht"),
  ], [("Latin","digitus","finger"),("Greek","daktylos","finger"),("Sanskrit","hastaḥ","hand")]),

  ("këmbë", "leg, foot", "noun", "*ǵenh₁-", 0.84, [
    ("PIE","*ǵenh₁-"),("Proto-Albanian","*këmb-"),("Albanian","këmbë"),
  ], [("Latin","genu","knee"),("Greek","gónu","knee"),("Sanskrit","jānu","knee"),("English","knee","knee")]),

  ("shtat", "height, stature", "noun", "*steh₂-", 0.78, [
    ("PIE","*steh₂-"),("Proto-Albanian","*shtat-"),("Albanian","shtat"),
  ], [("Latin","statura","stature"),("Greek","stásis","standing"),("Sanskrit","sthāna","place")]),

  ("krah", "arm, wing", "noun", "*koro-", 0.75, [
    ("PIE","*koro-"),("Proto-Albanian","*krah-"),("Albanian","krah"),
  ], [("Latin","crus","leg"),("Greek","kṓlon","limb"),("Sanskrit","kara","hand")]),

  ("gjoks", "chest, breast", "noun", "*yeug-", 0.72, [
    ("PIE","*yeug-"),("Proto-Albanian","*gjoks-"),("Albanian","gjoks"),
  ], [("Latin","iugum","yoke"),("Greek","zeugos","pair"),("Sanskrit","yugas","yoke")]),

  ("hundë", "nose", "noun", "*sneudʰ-", 0.80, [
    ("PIE","*sneudʰ-"),("Proto-Albanian","*hund-"),("Albanian","hundë"),
  ], [("Latin","nasus","nose"),("Greek","nassō","to press"),("Sanskrit","nāsā","nose"),("English","nose","nose")]),

  ("vesh", "ear", "noun", "*h₂ewis-", 0.85, [
    ("PIE","*h₂ewis-"),("Proto-Albanian","*vesh-"),("Albanian","vesh"),
  ], [("Latin","auris","ear"),("Greek","oûs","ear"),("Sanskrit","karṇaḥ","ear"),("German","Ohr","ear")]),

  ("gjuhë", "tongue, language", "noun", "*dn̥ǵʰwéh₂s", 0.92, [
    ("PIE","*dn̥ǵʰwéh₂s"),("Proto-Albanian","*gjuh-"),("Albanian","gjuhë"),
  ], [("Latin","lingua","tongue"),("English","tongue","tongue"),("Gothic","tuggo","tongue"),("Lithuanian","liežuvis","tongue")]),

  ("dhëmb", "tooth", "noun", "*h₃dónts", 0.90, [
    ("PIE","*h₃dónts"),("Proto-Albanian","*dhëmb-"),("Albanian","dhëmb"),
  ], [("Latin","dens","tooth"),("Greek","odoús","tooth"),("Sanskrit","danta","tooth"),("English","tooth","tooth")]),

  ("sy", "eye", "noun", "*h₃okʷ-", 0.95, [
    ("PIE","*h₃okʷ-"),("Proto-Albanian","*sy-"),("Albanian","sy"),
  ], [("Latin","oculus","eye"),("Greek","opsis","sight"),("Sanskrit","akṣi","eye"),("English","eye","eye"),("Russian","oko","eye")]),

  ("vrimë", "hole, opening", "noun", "*wer-", 0.75, [
    ("PIE","*wer-"),("Proto-Albanian","*vrim-"),("Albanian","vrimë"),
  ], [("Latin","forare","to bore"),("Greek","pharynx","throat"),("English","worm","worm")]),

  # ── NATURE & LANDSCAPE ─────────────────────────────────────────────────────
  ("det", "sea", "noun", "*dʰewbʰ-", 0.82, [
    ("PIE","*dʰewbʰ-"),("Proto-Albanian","*det-"),("Albanian","det"),
  ], [("Greek","thalassa","sea"),("Latin","profundus","deep"),("Lithuanian","dubùs","deep")]),

  ("lumë", "river", "noun", "*lewbʰ-", 0.85, [
    ("PIE","*lewbʰ-"),("Proto-Albanian","*lum-"),("Albanian","lumë"),
  ], [("Latin","lumen","light, river"),("Greek","loúō","to wash"),("Sanskrit","lavati","washes")]),

  ("mal", "mountain", "noun", "*mol-", 0.82, [
    ("PIE","*mol-"),("Proto-Albanian","*mal-"),("Albanian","mal"),
  ], [("Latin","collis","hill"),("Greek","molóbros","glutton"),("Welsh","moel","bare hill")]),

  ("fushë", "field, plain", "noun", "*pleth₂-", 0.80, [
    ("PIE","*pleth₂-"),("Proto-Albanian","*fush-"),("Albanian","fushë"),
  ], [("Latin","planus","flat"),("Greek","platys","broad"),("Sanskrit","pṛthu","broad")]),

  ("tokë", "earth, ground", "noun", "*dhegʷʰom-", 0.88, [
    ("PIE","*dhegʷʰom-"),("Proto-Albanian","*tok-"),("Albanian","tokë"),
  ], [("Latin","humus","earth"),("Greek","khthṓn","earth"),("Sanskrit","kṣam-","earth")]),

  ("gurë", "stone, rock", "noun", "*gʷreh₂w-", 0.88, [
    ("PIE","*gʷreh₂w-"),("Proto-Albanian","*gur-"),("Albanian","gurë"),
  ], [("Latin","gravis","heavy"),("Greek","barys","heavy"),("Sanskrit","guru","heavy")]),

  ("rërë", "sand", "noun", "*h₂erH-", 0.78, [
    ("PIE","*h₂erH-"),("Proto-Albanian","*rër-"),("Albanian","rërë"),
  ], [("Latin","arena","sand"),("Greek","árēn","sand")]),

  ("baltë", "mud, clay", "noun", "*bʰel-", 0.75, [
    ("PIE","*bʰel-"),("Proto-Albanian","*balt-"),("Albanian","baltë"),
  ], [("Latin","fuligo","soot"),("Lithuanian","bala","swamp"),("Old Norse","ból","dwelling")]),

  ("shkëmb", "rock, cliff", "noun", "*skel-", 0.78, [
    ("PIE","*skel-"),("Proto-Albanian","*shkëmb-"),("Albanian","shkëmb"),
  ], [("Latin","scopulus","rock"),("Greek","skopelos","rock"),("Lithuanian","skelti","to cleave")]),

  ("lumtur", "happiness", "adjective", "*lewbʰ-", 0.72, [
    ("PIE","*lewbʰ-"),("Proto-Albanian","*lumt-"),("Albanian","lumtur"),
  ], [("Latin","lubet","it pleases"),("Gothic","liubs","dear")]),

  ("borë", "snow", "noun", "*bʰors-", 0.85, [
    ("PIE","*bʰors-"),("Proto-Albanian","*bor-"),("Albanian","borë"),
  ], [("Latin","furfur","bran"),("Russian","brus","whetstone"),("Lithuanian","barstýti","to scatter")]),

  ("akull", "ice", "noun", "*yeg-", 0.80, [
    ("PIE","*yeg-"),("Proto-Albanian","*akull-"),("Albanian","akull"),
  ], [("Latin","glacies","ice"),("Greek","kryos","cold"),("Sanskrit","yaj-","to freeze")]),

  ("zjarr", "fire", "noun", "*h₁egni-", 0.90, [
    ("PIE","*h₁egni-"),("Proto-Albanian","*zjarr-"),("Albanian","zjarr"),
  ], [("Latin","ignis","fire"),("Sanskrit","agni","fire"),("Lithuanian","ugnis","fire"),("Russian","ogon'","fire")]),

  ("erë", "wind", "noun", "*h₂weh₁-", 0.88, [
    ("PIE","*h₂weh₁-"),("Proto-Albanian","*er-"),("Albanian","erë"),
  ], [("Latin","ventus","wind"),("Greek","aḗr","air"),("Sanskrit","vāyuḥ","wind"),("English","wind","wind")]),

  ("re", "cloud", "noun", "*nebʰ-", 0.82, [
    ("PIE","*nebʰ-"),("Proto-Albanian","*re-"),("Albanian","re"),
  ], [("Latin","nebula","mist"),("Greek","nephos","cloud"),("Sanskrit","nabhas","sky"),("German","Nebel","fog")]),

  ("diell", "sun", "noun", "*sóh₂wl̥", 0.92, [
    ("PIE","*sóh₂wl̥"),("Proto-Albanian","*diel-"),("Albanian","diell"),
  ], [("Latin","sol","sun"),("Greek","hḗlios","sun"),("Sanskrit","sūrya","sun"),("English","sun","sun"),("Gothic","sauil","sun")]),

  ("hënë", "moon", "noun", "*mḗh₁n̥s", 0.90, [
    ("PIE","*mḗh₁n̥s"),("Proto-Albanian","*hën-"),("Albanian","hënë"),
  ], [("Latin","luna","moon"),("Greek","mḗnē","moon"),("Sanskrit","māsa","month"),("English","moon","moon"),("German","Mond","moon")]),

  ("natë", "night", "noun", "*nókʷts", 0.94, [
    ("PIE","*nókʷts"),("Proto-Albanian","*nat-"),("Albanian","natë"),
  ], [("Latin","nox","night"),("Greek","nýx","night"),("Sanskrit","nakt-","night"),("English","night","night"),("German","Nacht","night")]),

  ("ditë", "day", "noun", "*dyew-", 0.90, [
    ("PIE","*dyew-"),("Proto-Albanian","*dit-"),("Albanian","ditë"),
  ], [("Latin","dies","day"),("Sanskrit","diva","day"),("Greek","Zeus","sky-god")]),

  ("verë", "summer", "noun", "*wésr̥", 0.88, [
    ("PIE","*wésr̥"),("Proto-Albanian","*ver-"),("Albanian","verë"),
  ], [("Latin","ver","spring"),("Greek","éar","spring"),("Sanskrit","vasanta","spring"),("Russian","vesna","spring")]),

  ("dimër", "winter", "noun", "*ǵʰeymo-", 0.90, [
    ("PIE","*ǵʰeymo-"),("Proto-Albanian","*dimër-"),("Albanian","dimër"),
  ], [("Latin","hiems","winter"),("Greek","kheimṓn","winter"),("Sanskrit","hima","snow"),("Russian","zima","winter")]),

  ("pranverë", "spring", "noun", "*per-wésr̥", 0.85, [
    ("PIE","*per-wésr̥"),("Proto-Albanian","*pranver-"),("Albanian","pranverë"),
  ], [("Latin","ver","spring"),("Greek","éar","spring"),("Sanskrit","vasanta","spring")]),

  ("vjeshtë", "autumn", "noun", "*h₂ewg-", 0.78, [
    ("PIE","*h₂ewg-"),("Proto-Albanian","*vjesh-"),("Albanian","vjeshtë"),
  ], [("Latin","autumnus","autumn"),("Etruscan","𐌖𐌄𐌋𐌈𐌖𐌍𐌄","autumn")]),

  # ── FOOD & AGRICULTURE ─────────────────────────────────────────────────────
  ("bukë", "bread", "noun", "*bʰewHg-", 0.85, [
    ("PIE","*bʰewHg-"),("Proto-Albanian","*buk-"),("Albanian","bukë"),
  ], [("Latin","focus","hearth"),("German","backen","to bake"),("English","bake","to bake")]),

  ("kripë", "salt", "noun", "*sal-", 0.88, [
    ("PIE","*sal-"),("Proto-Albanian","*krip-"),("Albanian","kripë"),
  ], [("Latin","sal","salt"),("Greek","hals","salt"),("Russian","sol'","salt"),("English","salt","salt")]),

  ("mjaltë", "honey", "noun", "*melit-", 0.92, [
    ("PIE","*melit-"),("Proto-Albanian","*mjalt-"),("Albanian","mjaltë"),
  ], [("Latin","mel","honey"),("Greek","méli","honey"),("Sanskrit","madhu","honey"),("English","mildew","mildew")]),

  ("gjalpë", "butter", "noun", "*gal-p-", 0.78, [
    ("PIE","*gal-p-"),("Proto-Albanian","*gjalp-"),("Albanian","gjalpë"),
  ], [("Latin","lac","milk"),("Greek","gala","milk"),("Sanskrit","go","cow")]),

  ("qumësht", "milk", "noun", "*h₂melǵ-", 0.82, [
    ("PIE","*h₂melǵ-"),("Proto-Albanian","*qumësh-"),("Albanian","qumësht"),
  ], [("Greek","amélgō","to milk"),("Latin","mulgere","to milk"),("English","milk","milk"),("German","Milch","milk")]),

  ("djathë", "cheese", "noun", "*glag-", 0.78, [
    ("PIE","*glag-"),("Proto-Albanian","*djath-"),("Albanian","djathë"),
  ], [("Latin","lac","milk"),("Greek","gala","milk")]),

  ("verë", "wine", "noun", "*wóyh₁nom", 0.88, [
    ("PIE","*wóyh₁nom"),("Proto-Albanian","*ver-"),("Albanian","verë"),
  ], [("Latin","vinum","wine"),("Greek","oînos","wine"),("Armenian","gini","wine"),("Georgian","ɣvino","wine")]),

  ("birrë", "beer", "noun", "*bʰrewH-", 0.80, [
    ("PIE","*bʰrewH-"),("Proto-Albanian","*birr-"),("Albanian","birrë"),
  ], [("Latin","defrutum","boiled wine"),("English","brew","to brew"),("German","brauen","to brew")]),

  ("fasule", "bean", "noun", "*bʰakso-", 0.68, [
    ("PIE","*bʰakso-"),("Proto-Albanian","*fasul-"),("Albanian","fasule"),
  ], [("Latin","phaseolus","bean"),("Greek","phaselos","bean")]),

  ("domate", "tomato", "noun", "*dʰo-", 0.40, [
    ("Albanian","domate"),
  ], [("Italian","pomodoro","tomato"),("Spanish","tomate","tomato")]),

  ("patate", "potato", "noun", "*bhel-", 0.35, [
    ("Albanian","patate"),
  ], [("Spanish","patata","potato"),("Italian","patata","potato")]),

  ("mollë", "apple", "noun", "*meh₂lo-", 0.88, [
    ("PIE","*meh₂lo-"),("Proto-Albanian","*moll-"),("Albanian","mollë"),
  ], [("Latin","malum","apple"),("Greek","mêlon","apple"),("Welsh","afal","apple"),("Old Irish","ubull","apple")]),

  ("dardhë", "pear", "noun", "*dorH-", 0.82, [
    ("PIE","*dorH-"),("Proto-Albanian","*dardh-"),("Albanian","dardhë"),
  ], [("Latin","pirum","pear"),("Greek","ákras","wild pear"),("Welsh","gellyg","pear")]),

  ("rrush", "grape", "noun", "*rusko-", 0.75, [
    ("PIE","*rusko-"),("Proto-Albanian","*rrush-"),("Albanian","rrush"),
  ], [("Latin","ruscum","butcher's broom"),("Gaulish","*rusc-","bark")]),

  ("fiq", "fig", "noun", "*syko-", 0.65, [
    ("PIE","*syko-"),("Proto-Albanian","*fiq-"),("Albanian","fiq"),
  ], [("Latin","ficus","fig"),("Greek","sykon","fig")]),

  ("arra", "walnut", "noun", "*kary-", 0.78, [
    ("PIE","*kary-"),("Proto-Albanian","*arr-"),("Albanian","arra"),
  ], [("Greek","karyon","nut"),("Latin","nux","nut")]),

  # ── ANIMALS (extended) ─────────────────────────────────────────────────────
  ("qen", "dog", "noun", "*kʷon-", 0.95, [
    ("PIE","*kʷon-"),("Proto-Albanian","*qen-"),("Albanian","qen"),
  ], [("Latin","canis","dog"),("Greek","kýōn","dog"),("Sanskrit","śvā","dog"),("English","hound","dog"),("German","Hund","dog")]),

  ("mace", "cat", "noun", "*matth-", 0.65, [
    ("PIE","*matth-"),("Proto-Albanian","*mac-"),("Albanian","mace"),
  ], [("Latin","cattus","cat"),("Greek","kattos","cat"),("Arabic","qiṭṭ","cat")]),

  ("lopë", "cow", "noun", "*gwow-", 0.90, [
    ("PIE","*gwow-"),("Proto-Albanian","*lop-"),("Albanian","lopë"),
  ], [("Latin","bos","ox"),("Greek","boûs","ox"),("Sanskrit","go","cow"),("English","cow","cow")]),

  ("dem", "bull, ox", "noun", "*dʰewbʰ-", 0.82, [
    ("PIE","*dʰewbʰ-"),("Proto-Albanian","*dem-"),("Albanian","dem"),
  ], [("Latin","taurus","bull"),("Greek","taûros","bull"),("Sanskrit","sthūra","bull")]),

  ("kal", "horse", "noun", "*kabalos-", 0.85, [
    ("PIE","*kabalos-"),("Proto-Albanian","*kal-"),("Albanian","kalë"),
  ], [("Latin","caballus","horse"),("Greek","kaballos","horse"),("Old Irish","capall","horse")]),

  ("dele", "sheep", "noun", "*h₂ówis", 0.90, [
    ("PIE","*h₂ówis"),("Proto-Albanian","*del-"),("Albanian","dele"),
  ], [("Latin","ovis","sheep"),("Greek","óis","sheep"),("Sanskrit","aviḥ","sheep"),("English","ewe","ewe"),("German","Schaf","sheep")]),

  ("dhi", "goat", "noun", "*gʰaido-", 0.88, [
    ("PIE","*gʰaido-"),("Proto-Albanian","*dhi-"),("Albanian","dhi"),
  ], [("Latin","haedus","kid"),("Gothic","gaits","goat"),("German","Geiß","goat"),("English","goat","goat")]),

  ("derr", "pig", "noun", "*sūs", 0.85, [
    ("PIE","*sūs"),("Proto-Albanian","*derr-"),("Albanian","derr"),
  ], [("Latin","sus","pig"),("Greek","hys","pig"),("Sanskrit","sūkara","pig"),("English","sow","sow"),("German","Sau","sow")]),

  ("gjel", "rooster, cock", "noun", "*gal-", 0.78, [
    ("PIE","*gal-"),("Proto-Albanian","*gjel-"),("Albanian","gjel"),
  ], [("Latin","gallus","rooster"),("Welsh","ceiliog","rooster"),("Old Irish","cailech","rooster")]),

  ("pulë", "hen", "noun", "*pulo-", 0.80, [
    ("PIE","*pulo-"),("Proto-Albanian","*pul-"),("Albanian","pulë"),
  ], [("Latin","pullus","chick"),("Greek","pōlos","foal"),("French","poule","hen")]),

  ("patë", "duck", "noun", "*poti-", 0.75, [
    ("PIE","*poti-"),("Proto-Albanian","*pat-"),("Albanian","patë"),
  ], [("Latin","anas","duck"),("Greek","nēssa","duck"),("Sanskrit","ātī","duck")]),

  ("mjellmë", "swan", "noun", "*mel-", 0.80, [
    ("PIE","*mel-"),("Proto-Albanian","*mjellm-"),("Albanian","mjellmë"),
  ], [("English","mellow","mellow"),("Latin","melinus","quince-yellow")]),

  ("shpend", "bird", "noun", "*spendʰ-", 0.78, [
    ("PIE","*spendʰ-"),("Proto-Albanian","*shpend-"),("Albanian","shpend"),
  ], [("Latin","penna","feather"),("Greek","pterón","wing"),("Sanskrit","patati","flies")]),

  ("zog", "bird, chick", "noun", "*ǵʰo-", 0.72, [
    ("PIE","*ǵʰo-"),("Proto-Albanian","*zog-"),("Albanian","zog"),
  ], [("Latin","gallus","rooster"),("Greek","goos","voice")]),

  ("gjarpër", "snake", "noun", "*serpens", 0.85, [
    ("PIE","*serp-"),("Proto-Albanian","*gjarp-"),("Albanian","gjarpër"),
  ], [("Latin","serpens","serpent"),("Greek","herpetón","reptile"),("Sanskrit","sarpati","crawls")]),

  ("bretkosë", "frog", "noun", "*bʰrek-", 0.75, [
    ("PIE","*bʰrek-"),("Proto-Albanian","*bretk-"),("Albanian","bretkosë"),
  ], [("Latin","rana","frog"),("Greek","batrakhos","frog"),("German","Frosch","frog")]),

  ("peshk", "fish", "noun", "*peisk-", 0.88, [
    ("PIE","*peisk-"),("Proto-Albanian","*peshk-"),("Albanian","peshk"),
  ], [("Latin","piscis","fish"),("Gothic","fisks","fish"),("English","fish","fish"),("German","Fisch","fish")]),

  ("milingonë", "ant", "noun", "*morwi-", 0.80, [
    ("PIE","*morwi-"),("Proto-Albanian","*miling-"),("Albanian","milingonë"),
  ], [("Latin","formica","ant"),("Greek","mýrmēx","ant"),("Sanskrit","vamrī","ant")]),

  ("mizë", "fly (insect)", "noun", "*mus-", 0.82, [
    ("PIE","*mus-"),("Proto-Albanian","*miz-"),("Albanian","mizë"),
  ], [("Latin","musca","fly"),("Greek","myia","fly"),("Russian","mukha","fly"),("English","midge","midge")]),

  ("neçka", "bee", "noun", "*bʰei-", 0.70, [
    ("PIE","*bʰei-"),("Proto-Albanian","*blet-"),("Albanian","neçka"),
  ], [("Latin","apis","bee"),("Greek","melissa","bee"),("Old Irish","bech","bee")]),

  ("ujk", "wolf", "noun", "*wĺ̥kʷos", 0.94, [
    ("PIE","*wĺ̥kʷos"),("Proto-Albanian","*ulk-"),("Albanian","ujk"),
  ], [("Latin","lupus","wolf"),("Greek","lýkos","wolf"),("Sanskrit","vṛkas","wolf"),("Russian","volk","wolf"),("German","Wolf","wolf")]),

  ("ariu", "bear", "noun", "*h₂ŕ̥tḱos", 0.90, [
    ("PIE","*h₂ŕ̥tḱos"),("Proto-Albanian","*ari-"),("Albanian","ariu"),
  ], [("Latin","ursus","bear"),("Greek","árktos","bear"),("Sanskrit","ṛkṣa","bear"),("Welsh","arth","bear")]),

  ("dhelpër", "fox", "noun", "*albʰo-", 0.75, [
    ("PIE","*albʰo-"),("Proto-Albanian","*dhelp-"),("Albanian","dhelpër"),
  ], [("Latin","vulpes","fox"),("Greek","alōpēx","fox"),("Sanskrit","lopāśa","jackal")]),

  ("dreri", "deer", "noun", "*dhreugh-", 0.82, [
    ("PIE","*dhreugh-"),("Proto-Albanian","*drer-"),("Albanian","dre"),
  ], [("Latin","cervus","deer"),("Greek","élaphos","deer"),("Sanskrit","hariṇa","deer"),("English","deer","deer")]),

  ("lepuri", "hare, rabbit", "noun", "*lep-", 0.78, [
    ("PIE","*lep-"),("Proto-Albanian","*lepur-"),("Albanian","lepuri"),
  ], [("Latin","lepus","hare"),("Greek","lagōós","hare"),("Lithuanian","lape","fox")]),

  # ── TOOLS & OBJECTS ────────────────────────────────────────────────────────
  ("thikë", "knife", "noun", "*teyǵ-", 0.82, [
    ("PIE","*teyǵ-"),("Proto-Albanian","*thik-"),("Albanian","thikë"),
  ], [("Greek","stígma","mark"),("Latin","in-stinguere","to incite"),("English","stick","stick")]),

  ("lugë", "spoon", "noun", "*lewgh-", 0.75, [
    ("PIE","*lewgh-"),("Proto-Albanian","*lug-"),("Albanian","lugë"),
  ], [("Latin","lingere","to lick"),("Greek","leikhō","to lick"),("English","lick","to lick")]),

  ("enë", "vessel, dish", "noun", "*h₁en-", 0.80, [
    ("PIE","*h₁en-"),("Proto-Albanian","*en-"),("Albanian","enë"),
  ], [("Latin","in","in"),("Greek","en","in"),("Sanskrit","in","in")]),

  ("parmendë", "plow", "noun", "*por-men-", 0.82, [
    ("PIE","*por-men-"),("Proto-Albanian","*parmen-"),("Albanian","parmendë"),
  ], [("Latin","porca","ridge"),("Greek","peira","trial"),("Sanskrit","para","far")]),

  ("sharrë", "saw (tool)", "noun", "*sker-", 0.78, [
    ("PIE","*sker-"),("Proto-Albanian","*sharr-"),("Albanian","sharrë"),
  ], [("Latin","secare","to cut"),("English","shear","to shear"),("German","scheren","to shear")]),

  ("potkua", "horseshoe", "noun", "*pod-", 0.68, [
    ("PIE","*pod-"),("Proto-Albanian","*potk-"),("Albanian","potkua"),
  ], [("Latin","pes","foot"),("Greek","poús","foot"),("Sanskrit","pāda","foot")]),

  ("litë", "rope", "noun", "*leit-", 0.72, [
    ("PIE","*leit-"),("Proto-Albanian","*lit-"),("Albanian","litë"),
  ], [("Latin","linea","line"),("Greek","linon","flax"),("English","line","line")]),

  ("shtizë", "spear", "noun", "*steyg-", 0.85, [
    ("PIE","*steyg-"),("Proto-Albanian","*shtiz-"),("Albanian","shtizë"),
  ], [("Greek","stizō","to prick"),("Latin","in-stinguere","to incite"),("German","Stachel","spine")]),

  ("shigjetë", "arrow", "noun", "*skegh-", 0.78, [
    ("PIE","*skegh-"),("Proto-Albanian","*shigjt-"),("Albanian","shigjetë"),
  ], [("Latin","sagitta","arrow"),("Greek","belos","arrow")]),

  ("mburojë", "shield", "noun", "*bhoro-", 0.75, [
    ("PIE","*bhoro-"),("Proto-Albanian","*mbur-"),("Albanian","mburojë"),
  ], [("Latin","parma","shield"),("Greek","parmē","shield")]),

  # ── NUMBERS ────────────────────────────────────────────────────────────────
  ("një", "one", "numeral", "*óynos", 0.92, [
    ("PIE","*óynos"),("Proto-Albanian","*nj-"),("Albanian","një"),
  ], [("Latin","unus","one"),("Greek","oînos","one on dice"),("Gothic","ains","one"),("English","one","one")]),

  ("dy", "two", "numeral", "*dwóh₁", 0.96, [
    ("PIE","*dwóh₁"),("Proto-Albanian","*dy-"),("Albanian","dy"),
  ], [("Latin","duo","two"),("Greek","dúo","two"),("Sanskrit","dvā","two"),("English","two","two"),("Russian","dva","two")]),

  ("tre", "three", "numeral", "*tréyes", 0.95, [
    ("PIE","*tréyes"),("Proto-Albanian","*tri-"),("Albanian","tre"),
  ], [("Latin","tres","three"),("Greek","treîs","three"),("Sanskrit","trī","three"),("English","three","three"),("Russian","tri","three")]),

  ("katër", "four", "numeral", "*kʷetwóres", 0.94, [
    ("PIE","*kʷetwóres"),("Proto-Albanian","*katër-"),("Albanian","katër"),
  ], [("Latin","quattuor","four"),("Greek","téssares","four"),("Sanskrit","catvāras","four"),("English","four","four")]),

  ("pesë", "five", "numeral", "*pénkʷe", 0.95, [
    ("PIE","*pénkʷe"),("Proto-Albanian","*pës-"),("Albanian","pesë"),
  ], [("Latin","quinque","five"),("Greek","pénte","five"),("Sanskrit","pañca","five"),("English","five","five"),("Russian","pyat'","five")]),

  ("gjashtë", "six", "numeral", "*swéks", 0.90, [
    ("PIE","*swéks"),("Proto-Albanian","*gjasht-"),("Albanian","gjashtë"),
  ], [("Latin","sex","six"),("Greek","héx","six"),("Sanskrit","ṣaṣ","six"),("English","six","six")]),

  ("shtatë", "seven", "numeral", "*septḿ̥", 0.92, [
    ("PIE","*septḿ̥"),("Proto-Albanian","*shtat-"),("Albanian","shtatë"),
  ], [("Latin","septem","seven"),("Greek","heptá","seven"),("Sanskrit","sapta","seven"),("English","seven","seven")]),

  ("tetë", "eight", "numeral", "*oḱtṓ", 0.91, [
    ("PIE","*oḱtṓ"),("Proto-Albanian","*tet-"),("Albanian","tetë"),
  ], [("Latin","octo","eight"),("Greek","oktṓ","eight"),("Sanskrit","aṣṭa","eight"),("English","eight","eight")]),

  ("nëntë", "nine", "numeral", "*h₁néwn̥", 0.90, [
    ("PIE","*h₁néwn̥"),("Proto-Albanian","*nënt-"),("Albanian","nëntë"),
  ], [("Latin","novem","nine"),("Greek","ennéa","nine"),("Sanskrit","nava","nine"),("English","nine","nine")]),

  ("dhjetë", "ten", "numeral", "*déḱm̥t", 0.93, [
    ("PIE","*déḱm̥t"),("Proto-Albanian","*dhjt-"),("Albanian","dhjetë"),
  ], [("Latin","decem","ten"),("Greek","déka","ten"),("Sanskrit","daśa","ten"),("English","ten","ten"),("Russian","desyat'","ten")]),

  # ── ADJECTIVES ─────────────────────────────────────────────────────────────
  ("i ri", "new, young", "adjective", "*new-yo-", 0.88, [
    ("PIE","*new-yo-"),("Proto-Albanian","*ri-"),("Albanian","i ri"),
  ], [("Latin","novus","new"),("Greek","néos","new"),("Sanskrit","navas","new"),("English","new","new"),("Russian","novyj","new")]),

  ("i vjetër", "old", "adjective", "*wetus-", 0.88, [
    ("PIE","*wetus-"),("Proto-Albanian","*vjetër-"),("Albanian","i vjetër"),
  ], [("Latin","vetus","old"),("Greek","étos","year"),("Sanskrit","vatsa","year-old calf")]),

  ("i madh", "big, great", "adjective", "*meǵ-", 0.92, [
    ("PIE","*meǵ-"),("Proto-Albanian","*madh-"),("Albanian","i madh"),
  ], [("Latin","magnus","great"),("Greek","mégas","great"),("Sanskrit","mahat","great"),("English","much","much")]),

  ("i vogël", "small, little", "adjective", "*wokelo-", 0.80, [
    ("PIE","*wokelo-"),("Proto-Albanian","*vogël-"),("Albanian","i vogël"),
  ], [("Latin","pusillus","tiny"),("Greek","pōu","little")]),

  ("i bardhë", "white", "adjective", "*bʰel-", 0.88, [
    ("PIE","*bʰel-"),("Proto-Albanian","*bardh-"),("Albanian","i bardhë"),
  ], [("Latin","fulvus","tawny"),("Greek","phalos","white"),("Sanskrit","bhāla","brightness"),("English","bald","bald")]),

  ("i zi", "black", "adjective", "*ǵʰel-", 0.80, [
    ("PIE","*ǵʰel-"),("Proto-Albanian","*zi-"),("Albanian","i zi"),
  ], [("Latin","helvus","honey-yellow"),("Greek","khlōrós","green"),("Lithuanian","žalias","green")]),

  ("i kuq", "red", "adjective", "*krewh₂-", 0.82, [
    ("PIE","*krewh₂-"),("Proto-Albanian","*kuq-"),("Albanian","i kuq"),
  ], [("Latin","cruor","blood"),("Greek","kréas","flesh"),("Sanskrit","kraviḥ","raw flesh"),("English","raw","raw")]),

  ("i gjelbër", "green", "adjective", "*ǵʰelh₃-", 0.82, [
    ("PIE","*ǵʰelh₃-"),("Proto-Albanian","*gjelbër-"),("Albanian","i gjelbër"),
  ], [("Latin","helvus","honey-yellow"),("Greek","khlōrós","green"),("English","yellow","yellow"),("German","gelb","yellow")]),

  ("i kaltër", "blue", "adjective", "*kʷel-", 0.75, [
    ("PIE","*kʷel-"),("Proto-Albanian","*kaltër-"),("Albanian","i kaltër"),
  ], [("Greek","kyanos","dark blue"),("Latin","caelum","sky"),("Sanskrit","śyāvas","dark")]),

  ("i fortë", "strong, hard", "adjective", "*bʰorgʰ-", 0.80, [
    ("PIE","*bʰorgʰ-"),("Proto-Albanian","*fort-"),("Albanian","i fortë"),
  ], [("Latin","fortis","strong"),("Greek","bíā","force"),("Sanskrit","bala","strength")]),

  ("i butë", "soft, gentle", "adjective", "*bʰudʰ-", 0.78, [
    ("PIE","*bʰudʰ-"),("Proto-Albanian","*but-"),("Albanian","i butë"),
  ], [("Latin","futilis","brittle"),("Greek","puthō","to rot")]),

  ("i gjatë", "tall, long", "adjective", "*dʰolǵʰo-", 0.82, [
    ("PIE","*dʰolǵʰo-"),("Proto-Albanian","*gjat-"),("Albanian","i gjatë"),
  ], [("Latin","longus","long"),("Greek","dolikhos","long"),("Sanskrit","dīrgha","long"),("English","long","long")]),

  ("i shkurtër", "short", "adjective", "*skerH-", 0.78, [
    ("PIE","*skerH-"),("Proto-Albanian","*shkurt-"),("Albanian","i shkurtër"),
  ], [("Latin","curtus","short"),("Greek","keirō","to cut"),("English","short","short")]),

  ("i ngrohtë", "warm", "adjective", "*gʷʰer-", 0.82, [
    ("PIE","*gʷʰer-"),("Proto-Albanian","*ngroht-"),("Albanian","i ngrohtë"),
  ], [("Latin","formus","warm"),("Greek","thermós","hot"),("Sanskrit","gharma","heat"),("English","warm","warm")]),

  ("i ftohtë", "cold", "adjective", "*stelH-", 0.80, [
    ("PIE","*stelH-"),("Proto-Albanian","*ftoh-"),("Albanian","i ftohtë"),
  ], [("Latin","gelidus","icy"),("Greek","stelein","to freeze"),("English","cold","cold")]),

  ("i vjetër", "old (thing)", "adjective", "*wetus-", 0.85, [
    ("PIE","*wetus-"),("Proto-Albanian","*vjetr-"),("Albanian","i vjetër"),
  ], [("Latin","vetus","old"),("Greek","étos","year"),("Sanskrit","vatsa","year")]),

  ("i mirë", "good", "adjective", "*mel-", 0.82, [
    ("PIE","*mel-"),("Proto-Albanian","*mir-"),("Albanian","i mirë"),
  ], [("Greek","mélas","black"),("Latin","malum","evil"),("Sanskrit","mala","impurity")]),

  ("i keq", "bad, evil", "adjective", "*kakos-", 0.70, [
    ("PIE","*kakos-"),("Proto-Albanian","*keq-"),("Albanian","i keq"),
  ], [("Greek","kakós","bad"),("Latin","cacare","to defecate")]),

  ("i shpejtë", "fast, quick", "adjective", "*spey-", 0.78, [
    ("PIE","*spey-"),("Proto-Albanian","*shpejt-"),("Albanian","i shpejtë"),
  ], [("Latin","spes","hope"),("Greek","speúdō","to hurry"),("Sanskrit","sphāyate","grows")]),

  ("i ngadaltë", "slow", "adjective", "*ni-gʷhedʰ-", 0.70, [
    ("PIE","*ni-gʷhedʰ-"),("Proto-Albanian","*ngadalt-"),("Albanian","i ngadaltë"),
  ], [("Latin","gradus","step"),("Greek","baínō","to go")]),

  # ── KINSHIP (extended) ─────────────────────────────────────────────────────
  ("baba", "father (familiar)", "noun", "*pəter-", 0.88, [
    ("PIE","*pəter-"),("Proto-Albanian","*bab-"),("Albanian","baba"),
  ], [("Latin","pater","father"),("Greek","patḗr","father"),("Sanskrit","pitā","father"),("English","father","father")]),

  ("nënë", "mother", "noun", "*méh₂tēr", 0.92, [
    ("PIE","*méh₂tēr"),("Proto-Albanian","*nën-"),("Albanian","nënë"),
  ], [("Latin","mater","mother"),("Greek","mḗtēr","mother"),("Sanskrit","mātā","mother"),("English","mother","mother")]),

  ("vëlla", "brother", "noun", "*bʰréh₂tēr", 0.90, [
    ("PIE","*bʰréh₂tēr"),("Proto-Albanian","*vëll-"),("Albanian","vëlla"),
  ], [("Latin","frater","brother"),("Greek","phratḗr","clansman"),("Sanskrit","bhrātā","brother"),("English","brother","brother")]),

  ("motër", "sister", "noun", "*swésōr", 0.90, [
    ("PIE","*swésōr"),("Proto-Albanian","*motër-"),("Albanian","motër"),
  ], [("Latin","soror","sister"),("Sanskrit","svasar","sister"),("English","sister","sister"),("Russian","sestra","sister")]),

  ("bir", "son", "noun", "*bʰer-", 0.85, [
    ("PIE","*bʰer-"),("Proto-Albanian","*bir-"),("Albanian","bir"),
  ], [("Sanskrit","bhṛta","carried"),("Gothic","bairan","to bear"),("English","bear","to bear")]),

  ("bijë", "daughter", "noun", "*dʰugʰh₂tḗr", 0.88, [
    ("PIE","*dʰugʰh₂tḗr"),("Proto-Albanian","*bij-"),("Albanian","bijë"),
  ], [("Greek","thygátēr","daughter"),("Sanskrit","duhitā","daughter"),("German","Tochter","daughter"),("English","daughter","daughter")]),

  ("gjysh", "grandfather", "noun", "*ǵen-", 0.80, [
    ("PIE","*ǵen-"),("Proto-Albanian","*gjysh-"),("Albanian","gjysh"),
  ], [("Latin","genus","birth"),("Greek","génos","race"),("Sanskrit","janas","people")]),

  ("gjyshe", "grandmother", "noun", "*ǵen-", 0.78, [
    ("PIE","*ǵen-"),("Proto-Albanian","*gjysh-"),("Albanian","gjyshe"),
  ], [("Latin","genus","birth"),("Greek","génos","race")]),

  ("nipë", "nephew, grandson", "noun", "*nepot-", 0.88, [
    ("PIE","*nepot-"),("Proto-Albanian","*nip-"),("Albanian","nipë"),
  ], [("Latin","nepos","grandson"),("Sanskrit","napāt","descendant"),("English","nephew","nephew"),("German","Neffe","nephew")]),

  ("mbesë", "niece, granddaughter", "noun", "*nepot-", 0.82, [
    ("PIE","*nepot-"),("Proto-Albanian","*mbes-"),("Albanian","mbesë"),
  ], [("Latin","neptis","niece"),("Sanskrit","naptrī","granddaughter")]),

  ("vjehër", "father-in-law", "noun", "*swek̑uro-", 0.90, [
    ("PIE","*swek̑uro-"),("Proto-Albanian","*vjehër-"),("Albanian","vjehër"),
  ], [("Latin","socer","father-in-law"),("Greek","hekurós","father-in-law"),("Sanskrit","śvaśura","father-in-law"),("Russian","svekor","father-in-law")]),

  ("vjehërë", "mother-in-law", "noun", "*swek̑ruh₂-", 0.88, [
    ("PIE","*swek̑ruh₂-"),("Proto-Albanian","*vjehër-"),("Albanian","vjehërë"),
  ], [("Latin","socrus","mother-in-law"),("Greek","hekyrá","mother-in-law"),("Sanskrit","śvaśrū","mother-in-law")]),

  ("nuse", "bride, daughter-in-law", "noun", "*snusó-", 0.90, [
    ("PIE","*snusó-"),("Proto-Albanian","*nuse-"),("Albanian","nuse"),
  ], [("Greek","nyós","daughter-in-law"),("Sanskrit","snuṣā","daughter-in-law"),("Russian","nevesta","bride"),("German","Schnur","daughter-in-law")]),

  ("dhëndër", "son-in-law, bridegroom", "noun", "*ǵʰemo-", 0.82, [
    ("PIE","*ǵʰemo-"),("Proto-Albanian","*dhëndër-"),("Albanian","dhëndër"),
  ], [("Greek","gambrós","son-in-law"),("Latin","gener","son-in-law"),("Sanskrit","jāmātā","son-in-law")]),

  ("kushëri", "cousin", "noun", "*kon-sek-", 0.72, [
    ("PIE","*kon-sek-"),("Proto-Albanian","*kush-"),("Albanian","kushëri"),
  ], [("Latin","consobrinus","cousin"),("French","cousin","cousin")]),

  ("fëmijë", "child", "noun", "*dʰēy-", 0.78, [
    ("PIE","*dʰēy-"),("Proto-Albanian","*fëmij-"),("Albanian","fëmijë"),
  ], [("Greek","thēlus","female"),("Sanskrit","dhayati","sucks")]),

  # ── ABSTRACT & SOCIETY ─────────────────────────────────────────────────────
  ("jetë", "life", "noun", "*gʷeyH-", 0.88, [
    ("PIE","*gʷeyH-"),("Proto-Albanian","*jet-"),("Albanian","jetë"),
  ], [("Greek","bíos","life"),("Latin","vita","life"),("Sanskrit","jīvita","life"),("English","quick","alive")]),

  ("vdekje", "death", "noun", "*dhwes-", 0.82, [
    ("PIE","*dhwes-"),("Proto-Albanian","*vdek-"),("Albanian","vdekje"),
  ], [("Greek","thanatos","death"),("Latin","mors","death"),("Sanskrit","mṛtyu","death")]),

  ("dashuri", "love", "noun", "*dʰewbʰ-", 0.75, [
    ("PIE","*dʰewbʰ-"),("Proto-Albanian","*dashur-"),("Albanian","dashuri"),
  ], [("Latin","amor","love"),("Greek","éros","love"),("Sanskrit","kāma","desire")]),

  ("urrejtje", "hatred", "noun", "*h₁wers-", 0.70, [
    ("PIE","*h₁wers-"),("Proto-Albanian","*urre-"),("Albanian","urrejtje"),
  ], [("Gothic","wrathjan","to anger"),("English","wrath","wrath")]),

  ("gëzim", "joy", "noun", "*gʷʰedʰ-", 0.72, [
    ("PIE","*gʷʰedʰ-"),("Proto-Albanian","*gëzim-"),("Albanian","gëzim"),
  ], [("Greek","agathós","good"),("Sanskrit","gadha","strong")]),

  ("frikë", "fear", "noun", "*preyH-", 0.75, [
    ("PIE","*preyH-"),("Proto-Albanian","*frik-"),("Albanian","frikë"),
  ], [("Latin","perīculum","danger"),("Greek","peîra","attempt"),("Sanskrit","priya","dear")]),

  ("kujtesë", "memory", "noun", "*koyt-", 0.72, [
    ("PIE","*koyt-"),("Proto-Albanian","*kujt-"),("Albanian","kujtesë"),
  ], [("Latin","cogitare","to think"),("Greek","koeō","to perceive")]),

  ("kohë", "time", "noun", "*kweh₂-", 0.78, [
    ("PIE","*kweh₂-"),("Proto-Albanian","*koh-"),("Albanian","kohë"),
  ], [("Latin","quando","when"),("Greek","pote","when"),("Sanskrit","kadā","when")]),

  ("vend", "place", "noun", "*wendʰ-", 0.78, [
    ("PIE","*wendʰ-"),("Proto-Albanian","*vend-"),("Albanian","vend"),
  ], [("Latin","endo","into"),("Greek","éndon","within"),("Sanskrit","antar","within")]),

  ("rrugë", "road, way", "noun", "*h₃reǵ-", 0.80, [
    ("PIE","*h₃reǵ-"),("Proto-Albanian","*rrug-"),("Albanian","rrugë"),
  ], [("Latin","regere","to rule"),("Greek","orégō","to reach"),("Sanskrit","ṛjyati","goes straight")]),

  ("fshat", "village", "noun", "*wik-", 0.78, [
    ("PIE","*wik-"),("Proto-Albanian","*fshat-"),("Albanian","fshat"),
  ], [("Latin","vicus","village"),("Greek","oikos","house"),("Sanskrit","viś","settlement")]),

  ("qytet", "city, town", "noun", "*kʷey-", 0.72, [
    ("PIE","*kʷey-"),("Proto-Albanian","*qytet-"),("Albanian","qytet"),
  ], [("Latin","civis","citizen"),("Greek","keîmai","to lie"),("Sanskrit","ci-","to heap")]),

  ("komb", "nation, people", "noun", "*komonos-", 0.75, [
    ("PIE","*komonos-"),("Proto-Albanian","*komb-"),("Albanian","komb"),
  ], [("Latin","communis","common"),("Gothic","gamains","common"),("English","common","common")]),

  ("ligj", "law", "noun", "*leǵ-", 0.80, [
    ("PIE","*leǵ-"),("Proto-Albanian","*ligj-"),("Albanian","ligj"),
  ], [("Latin","lex","law"),("Greek","légō","to speak"),("English","legal","legal")]),

  ("luftë", "war, battle", "noun", "*lew-bʰ-", 0.75, [
    ("PIE","*lew-bʰ-"),("Proto-Albanian","*luft-"),("Albanian","luftë"),
  ], [("Gothic","liufs","dear"),("German","Lob","praise"),("Latin","lubet","it pleases")]),

  ("paqe", "peace", "noun", "*pak-", 0.80, [
    ("PIE","*pak-"),("Proto-Albanian","*paq-"),("Albanian","paqe"),
  ], [("Latin","pax","peace"),("Latin","pangere","to fasten"),("English","pact","pact")]),

  ("mëkë", "sin, fault", "noun", "*meǵ-", 0.65, [
    ("PIE","*meǵ-"),("Proto-Albanian","*mëk-"),("Albanian","mëkë"),
  ], [("Latin","malum","evil"),("Greek","mélas","black")]),

  ("besë", "faith, oath", "noun", "*bʰedʰ-", 0.78, [
    ("PIE","*bʰedʰ-"),("Proto-Albanian","*bes-"),("Albanian","besë"),
  ], [("Latin","fides","faith"),("Greek","peíthomai","to be persuaded"),("Sanskrit","bādhate","presses")]),

  ("dije", "knowledge", "noun", "*woid-", 0.82, [
    ("PIE","*woid-"),("Proto-Albanian","*dij-"),("Albanian","dije"),
  ], [("Latin","videre","to see"),("Greek","oîda","I know"),("Sanskrit","veda","knowledge"),("English","wise","wise")]),

  ("botë", "world", "noun", "*bʰudʰ-", 0.72, [
    ("PIE","*bʰudʰ-"),("Proto-Albanian","*bot-"),("Albanian","botë"),
  ], [("Sanskrit","budh-","to awaken"),("English","bide","to wait")]),

  ("liri", "freedom", "noun", "*leudʰ-", 0.78, [
    ("PIE","*leudʰ-"),("Proto-Albanian","*lir-"),("Albanian","liri"),
  ], [("Latin","liber","free"),("Greek","eleútheros","free"),("Gothic","liudan","to grow")]),

  ("shpirt", "spirit, soul", "noun", "*spir-", 0.72, [
    ("PIE","*spir-"),("Proto-Albanian","*shpirt-"),("Albanian","shpirt"),
  ], [("Latin","spiritus","breath"),("Greek","psychē","soul"),("Sanskrit","prāṇa","breath")]),

  ("zë", "voice, sound", "noun", "*gʷʰow-", 0.80, [
    ("PIE","*gʷʰow-"),("Proto-Albanian","*ze-"),("Albanian","zë"),
  ], [("Latin","vox","voice"),("Greek","ōpā","voice"),("Sanskrit","vāk","voice"),("English","voice","voice")]),

  ("emër", "name", "noun", "*h₁nómn̥", 0.92, [
    ("PIE","*h₁nómn̥"),("Proto-Albanian","*emër-"),("Albanian","emër"),
  ], [("Latin","nomen","name"),("Greek","ónoma","name"),("Sanskrit","nāman","name"),("English","name","name"),("German","Name","name")]),

  # ── PLANTS & TREES ─────────────────────────────────────────────────────────
  ("lule", "flower", "noun", "*leuk-", 0.78, [
    ("PIE","*leuk-"),("Proto-Albanian","*lul-"),("Albanian","lule"),
  ], [("Latin","lux","light"),("Greek","leukós","white"),("Sanskrit","rocaná","bright")]),

  ("bar", "grass", "noun", "*bʰors-", 0.80, [
    ("PIE","*bʰors-"),("Proto-Albanian","*bar-"),("Albanian","bar"),
  ], [("Latin","faenum","hay"),("Greek","botrys","cluster"),("Sanskrit","barhis","grass")]),

  ("thekër", "rye", "noun", "*sekH-", 0.78, [
    ("PIE","*sekH-"),("Proto-Albanian","*thekër-"),("Albanian","thekër"),
  ], [("Lithuanian","rugiai","rye"),("German","Roggen","rye"),("Russian","rozh'","rye")]),

  ("grurë", "wheat", "noun", "*gʷrh₂eno-", 0.85, [
    ("PIE","*gʷrh₂eno-"),("Proto-Albanian","*grur-"),("Albanian","grurë"),
  ], [("Latin","granum","grain"),("English","grain","grain"),("German","Korn","grain"),("Russian","zerno","grain")]),

  ("elb", "barley", "noun", "*albʰo-", 0.82, [
    ("PIE","*albʰo-"),("Proto-Albanian","*elb-"),("Albanian","elb"),
  ], [("Latin","albus","white"),("Greek","alphī","barley"),("Sanskrit","arbha","small")]),

  ("misër", "maize, corn", "noun", "*mesu-", 0.45, [
    ("Albanian","misër"),
  ], [("Turkish","mısır","Egypt, maize"),("Italian","meliga","millet")]),

  ("fier", "fern", "noun", "*pterH-", 0.80, [
    ("PIE","*pterH-"),("Proto-Albanian","*fier-"),("Albanian","fier"),
  ], [("Greek","pteris","fern"),("English","fern","fern"),("German","Farn","fern")]),

  ("bredh", "fir tree", "noun", "*bʰreg̑ʰ-", 0.82, [
    ("PIE","*bʰreg̑ʰ-"),("Proto-Albanian","*bredh-"),("Albanian","bredh"),
  ], [("Latin","fraxinus","ash tree"),("Gothic","brikum","I brake"),("German","Birke","birch")]),

  ("bung", "oak (type)", "noun", "*bʰah₂ǵos", 0.80, [
    ("PIE","*bʰah₂ǵos"),("Proto-Albanian","*bung-"),("Albanian","bung"),
  ], [("Latin","fagus","beech"),("Greek","phēgós","oak"),("German","Buche","beech"),("English","beech","beech")]),

  ("shelg", "willow", "noun", "*seli-", 0.78, [
    ("PIE","*seli-"),("Proto-Albanian","*shelg-"),("Albanian","shelg"),
  ], [("Latin","salix","willow"),("Greek","helikē","willow"),("English","sallow","willow")]),

  ("plepi", "poplar", "noun", "*plew-", 0.75, [
    ("PIE","*plew-"),("Proto-Albanian","*plep-"),("Albanian","plepi"),
  ], [("Latin","populus","poplar"),("Greek","leptos","peeled")]),

  ("thuprë", "reed, cane", "noun", "*tewp-", 0.72, [
    ("PIE","*tewp-"),("Proto-Albanian","*thupr-"),("Albanian","thuprë"),
  ], [("Greek","týphos","smoke"),("Latin","tubus","tube")]),

  # ── MISC / COMMON ──────────────────────────────────────────────────────────
  ("dhe", "and", "conjunction", "*gʰe", 0.82, [
    ("PIE","*gʰe"),("Proto-Albanian","*dhe"),("Albanian","dhe"),
  ], [("Greek","te","and"),("Sanskrit","ca","and"),("Latin","que","and")]),

  ("po", "yes; but", "particle", "*epo", 0.75, [
    ("PIE","*epo"),("Proto-Albanian","*po"),("Albanian","po"),
  ], [("Greek","epí","upon"),("Latin","ob","toward"),("Sanskrit","api","also")]),

  ("jo", "no, not", "particle", "*yō-", 0.78, [
    ("PIE","*yō-"),("Proto-Albanian","*jo"),("Albanian","jo"),
  ], [("Latin","iam","now"),("Sanskrit","yāvat","as long as")]),

  ("si", "how, as, like", "adverb", "*swē", 0.82, [
    ("PIE","*swē"),("Proto-Albanian","*si"),("Albanian","si"),
  ], [("Latin","se","himself"),("Greek","hōs","as"),("Sanskrit","svayam","self")]),

  ("ku", "where", "adverb", "*kʷo-", 0.85, [
    ("PIE","*kʷo-"),("Proto-Albanian","*ku"),("Albanian","ku"),
  ], [("Latin","quo","where"),("Greek","poû","where"),("Sanskrit","kva","where")]),

  ("kur", "when", "adverb", "*kʷo-r", 0.85, [
    ("PIE","*kʷo-r"),("Proto-Albanian","*kur"),("Albanian","kur"),
  ], [("Latin","cur","why"),("Greek","pote","when"),("Sanskrit","kadā","when")]),

  ("çfarë", "what (kind)", "pronoun", "*kʷe-", 0.78, [
    ("PIE","*kʷe-"),("Proto-Albanian","*çfar-"),("Albanian","çfarë"),
  ], [("Latin","qualis","what kind"),("Greek","poîos","what kind")]),

  ("kush", "who", "pronoun", "*kʷis", 0.88, [
    ("PIE","*kʷis"),("Proto-Albanian","*kush"),("Albanian","kush"),
  ], [("Latin","quis","who"),("Greek","tís","who"),("Sanskrit","kiḥ","who"),("English","who","who")]),

  ("çdo", "every, each", "pronoun", "*kʷo-dʰo", 0.75, [
    ("PIE","*kʷo-dʰo"),("Proto-Albanian","*çdo"),("Albanian","çdo"),
  ], [("Latin","quoddam","a certain"),("Greek","hodoús","road")]),

  ("asnjë", "none, nobody", "pronoun", "*ne-óynos", 0.75, [
    ("PIE","*ne-óynos"),("Proto-Albanian","*asnjë"),("Albanian","asnjë"),
  ], [("Latin","nemo","nobody"),("Greek","oudeís","nobody"),("Sanskrit","na","not")]),

  ("i gjithë", "all, whole", "adjective", "*gʷʰi-", 0.75, [
    ("PIE","*gʷʰi-"),("Proto-Albanian","*gjith-"),("Albanian","i gjithë"),
  ], [("Greek","bia","force"),("Sanskrit","hí","indeed")]),

  ("shumë", "many, much", "adverb", "*swomno-", 0.72, [
    ("PIE","*swomno-"),("Proto-Albanian","*shum-"),("Albanian","shumë"),
  ], [("Greek","soma","body"),("Latin","summa","sum")]),

  ("pak", "few, a little", "adverb", "*peh₂ko-", 0.75, [
    ("PIE","*peh₂ko-"),("Proto-Albanian","*pak"),("Albanian","pak"),
  ], [("Latin","paucus","few"),("Greek","paûros","few"),("Sanskrit","pauca","few")]),

  ("gjithmonë", "always", "adverb", "*gʷʰi-", 0.70, [
    ("PIE","*gʷʰi-"),("Proto-Albanian","*gjithmon-"),("Albanian","gjithmonë"),
  ], [("Latin","semper","always"),("Greek","aei","always"),("Sanskrit","sadā","always")]),

  ("kurrë", "never", "adverb", "*kʷo-r", 0.72, [
    ("PIE","*kʷo-r"),("Proto-Albanian","*kurr-"),("Albanian","kurrë"),
  ], [("Latin","neque","nor"),("Greek","oude","nor")]),

  ("tani", "now", "adverb", "*do-ni", 0.72, [
    ("PIE","*do-ni"),("Proto-Albanian","*tan-"),("Albanian","tani"),
  ], [("Latin","nunc","now"),("Greek","nyn","now"),("Sanskrit","nu","now")]),

  ("sot", "today", "adverb", "*so-dʰew-", 0.78, [
    ("PIE","*so-dʰew-"),("Proto-Albanian","*sot"),("Albanian","sot"),
  ], [("Latin","hodie","today"),("Greek","sḗmeron","today"),("Sanskrit","adya","today")]),

  ("nesër", "tomorrow", "adverb", "*ne-dhewHr-", 0.72, [
    ("PIE","*ne-dhewHr-"),("Proto-Albanian","*nesër"),("Albanian","nesër"),
  ], [("Latin","cras","tomorrow"),("Sanskrit","śvaḥ","tomorrow")]),

  ("dje", "yesterday", "adverb", "*dʰǵʰyés", 0.82, [
    ("PIE","*dʰǵʰyés"),("Proto-Albanian","*dj-"),("Albanian","dje"),
  ], [("Latin","heri","yesterday"),("Greek","khthés","yesterday"),("Sanskrit","hyas","yesterday"),("English","yesterday","yesterday")]),

  ("atëherë", "then, at that time", "adverb", "*to-dʰer-", 0.72, [
    ("PIE","*to-dʰer-"),("Proto-Albanian","*atëher-"),("Albanian","atëherë"),
  ], [("Latin","ibi","there"),("Greek","tote","then"),("Sanskrit","tadā","then")]),

  ("ndoshta", "perhaps, maybe", "adverb", "*n-dʰo-", 0.65, [
    ("PIE","*n-dʰo-"),("Proto-Albanian","*ndosht-"),("Albanian","ndoshta"),
  ], [("Latin","forsitan","perhaps"),("Greek","takhá","perhaps")]),

  ("gjë", "thing", "noun", "*ǵʰen-", 0.75, [
    ("PIE","*ǵʰen-"),("Proto-Albanian","*gjë"),("Albanian","gjë"),
  ], [("Latin","res","thing"),("Greek","khréma","thing"),("Sanskrit","jan-","to beget")]),

  ("punë", "work", "noun", "*pekʷ-", 0.78, [
    ("PIE","*pekʷ-"),("Proto-Albanian","*pun-"),("Albanian","punë"),
  ], [("Latin","opus","work"),("Greek","érgon","work"),("Sanskrit","apas","work")]),

  ("shtëpi", "home", "noun", "*stā-dhwi-", 0.80, [
    ("PIE","*stā-dhwi-"),("Proto-Albanian","*shtëp-"),("Albanian","shtëpi"),
  ], [("Latin","stabulum","stable"),("Greek","stásis","standing")]),

  ("muzikë", "music", "noun", "*mewsi-", 0.70, [
    ("PIE","*mewsi-"),("Proto-Albanian","*muzik-"),("Albanian","muzikë"),
  ], [("Greek","mousikē","music"),("Latin","musica","music")]),

  ("këngë", "song", "noun", "*kan-", 0.82, [
    ("PIE","*kan-"),("Proto-Albanian","*këng-"),("Albanian","këngë"),
  ], [("Latin","canere","to sing"),("Greek","kanakhē","ringing sound"),("Sanskrit","kan-","to sound")]),

  ("valle", "dance", "noun", "*wel-", 0.72, [
    ("PIE","*wel-"),("Proto-Albanian","*vall-"),("Albanian","valle"),
  ], [("Latin","volvere","to roll"),("Greek","eilýō","to roll")]),

  ("gur", "stone", "noun", "*gʷreh₂-", 0.88, [
    ("PIE","*gʷreh₂-"),("Proto-Albanian","*gur-"),("Albanian","gur"),
  ], [("Latin","gravis","heavy"),("Greek","barys","heavy"),("Sanskrit","guru","heavy")]),

  ("krua", "spring (water), fountain", "noun", "*krew-", 0.82, [
    ("PIE","*krew-"),("Proto-Albanian","*krua"),("Albanian","krua"),
  ], [("Greek","kréein","to flow"),("Latin","creare","to create"),("Sanskrit","kravya","raw flesh")]),

  ("pellg", "deep pool, lake", "noun", "*pelH-", 0.78, [
    ("PIE","*pelH-"),("Proto-Albanian","*pellg-"),("Albanian","pellg"),
  ], [("Greek","pélagos","sea"),("Latin","palus","marsh"),("Lithuanian","pelkė","swamp")]),

  ("brigë", "shore, bank", "noun", "*bʰregh-", 0.75, [
    ("PIE","*bʰregh-"),("Proto-Albanian","*brig-"),("Albanian","brigë"),
  ], [("Latin","ripa","bank"),("Gothic","bairgan","to protect"),("German","Berg","mountain")]),

  ("vaj", "oil", "noun", "*h₂ewg-", 0.75, [
    ("PIE","*h₂ewg-"),("Proto-Albanian","*vaj-"),("Albanian","vaj"),
  ], [("Latin","oleum","oil"),("Greek","élaion","olive oil"),("Sanskrit","ājya","clarified butter")]),

  ("dru", "wood, tree", "noun", "*dóru", 0.92, [
    ("PIE","*dóru"),("Proto-Albanian","*dru"),("Albanian","dru"),
  ], [("Greek","dóry","spear"),("Sanskrit","dāru","wood"),("English","tree","tree"),("Welsh","derw","oak")]),

  ("degë", "branch", "noun", "*dʰeigh-", 0.78, [
    ("PIE","*dʰeigh-"),("Proto-Albanian","*deg-"),("Albanian","degë"),
  ], [("Latin","fingo","to shape"),("Greek","toikhos","wall"),("Sanskrit","dehī","wall")]),

  ("rrënjë", "root (plant)", "noun", "*wreh₂d-", 0.82, [
    ("PIE","*wreh₂d-"),("Proto-Albanian","*rrënj-"),("Albanian","rrënjë"),
  ], [("Latin","radix","root"),("Greek","rhíza","root"),("Gothic","waurts","root"),("English","root","root")]),

  ("farë", "seed", "noun", "*sperH-", 0.80, [
    ("PIE","*sperH-"),("Proto-Albanian","*far-"),("Albanian","farë"),
  ], [("Latin","semen","seed"),("Greek","spéirein","to sow"),("English","spore","spore")]),

  ("frut", "fruit", "noun", "*bʰrug-", 0.78, [
    ("PIE","*bʰrug-"),("Proto-Albanian","*frut-"),("Albanian","frut"),
  ], [("Latin","fructus","fruit"),("Latin","frui","to enjoy"),("English","fruit","fruit")]),

  ("lëkurë", "skin, leather", "noun", "*skur-", 0.82, [
    ("PIE","*skur-"),("Proto-Albanian","*lëkur-"),("Albanian","lëkurë"),
  ], [("Latin","corium","hide"),("Greek","khorion","membrane"),("Lithuanian","skirti","to separate")]),

  ("gjak", "blood", "noun", "*yekʷr̥t-", 0.85, [
    ("PIE","*yekʷr̥t-"),("Proto-Albanian","*gjak-"),("Albanian","gjak"),
  ], [("Latin","iecur","liver"),("Greek","hêpar","liver"),("Sanskrit","yakṛt","liver")]),

  ("kockë", "bone", "noun", "*kost-", 0.88, [
    ("PIE","*kost-"),("Proto-Albanian","*kock-"),("Albanian","kockë"),
  ], [("Latin","costa","rib"),("Russian","kost'","bone"),("Old Irish","cnáim","bone")]),

  ("mëlçi", "liver", "noun", "*yekʷr̥t-", 0.82, [
    ("PIE","*yekʷr̥t-"),("Proto-Albanian","*mëlç-"),("Albanian","mëlçi"),
  ], [("Latin","iecur","liver"),("Greek","hêpar","liver"),("Sanskrit","yakṛt","liver"),("German","Leber","liver")]),

  ("zemër", "heart", "noun", "*ḱerd-", 0.92, [
    ("PIE","*ḱerd-"),("Proto-Albanian","*zemër-"),("Albanian","zemër"),
  ], [("Latin","cor","heart"),("Greek","kardíā","heart"),("Sanskrit","hṛd","heart"),("English","heart","heart"),("German","Herz","heart")]),

  ("veshkë", "kidney", "noun", "*nogʷʰ-", 0.72, [
    ("PIE","*nogʷʰ-"),("Proto-Albanian","*veshk-"),("Albanian","veshkë"),
  ], [("Latin","ren","kidney"),("Greek","nephrós","kidney"),("German","Niere","kidney")]),

  ("tru", "brain", "noun", "*dhrew-", 0.75, [
    ("PIE","*dhrew-"),("Proto-Albanian","*tru"),("Albanian","tru"),
  ], [("Greek","kránia","skull"),("Sanskrit","dharuṇa","support")]),

  ("fill", "thread, immediately", "noun", "*pilo-", 0.78, [
    ("PIE","*pilo-"),("Proto-Albanian","*fill-"),("Albanian","fill"),
  ], [("Latin","filum","thread"),("Greek","pilos","felt"),("English","file","file")]),

  ("shtof", "cloth, fabric", "noun", "*stobʰo-", 0.65, [
    ("PIE","*stobʰo-"),("Proto-Albanian","*shtof-"),("Albanian","shtof"),
  ], [("German","Stoff","fabric"),("Dutch","stof","fabric")]),

  ("qiri", "candle", "noun", "*kʷeyH-", 0.70, [
    ("PIE","*kʷeyH-"),("Proto-Albanian","*qir-"),("Albanian","qiri"),
  ], [("Greek","kḗrios","of wax"),("Latin","cera","wax")]),

  ("dhunë", "violence, force", "noun", "*dʰewbʰ-", 0.72, [
    ("PIE","*dʰewbʰ-"),("Proto-Albanian","*dhun-"),("Albanian","dhunë"),
  ], [("Latin","furere","to rage"),("Greek","thumos","spirit"),("Sanskrit","dhumas","smoke")]),

  ("qiell", "sky, heaven", "noun", "*kel-", 0.82, [
    ("PIE","*kel-"),("Proto-Albanian","*qiell-"),("Albanian","qiell"),
  ], [("Latin","caelum","sky"),("Greek","koîlos","hollow"),("Sanskrit","śāla","hall")]),

  ("dhe", "earth, land", "noun", "*dhegʷʰom-", 0.88, [
    ("PIE","*dhegʷʰom-"),("Proto-Albanian","*dh-"),("Albanian","dhe"),
  ], [("Latin","humus","earth"),("Greek","khthṓn","earth"),("Sanskrit","kṣam-","earth")]),

  ("ujë", "water", "noun", "*h₂ekʷeh₂-", 0.95, [
    ("PIE","*h₂ekʷeh₂-"),("Proto-Albanian","*uj-"),("Albanian","ujë"),
  ], [("Latin","aqua","water"),("Gothic","ahwa","water"),("Sanskrit","āpas","water"),("English","aqua","water")]),

  ("plumb", "lead (metal)", "noun", "*plombos-", 0.78, [
    ("PIE","*plombos-"),("Proto-Albanian","*plumb-"),("Albanian","plumb"),
  ], [("Latin","plumbum","lead"),("Greek","mólybdos","lead")]),

  ("hekur", "iron", "noun", "*isarno-", 0.80, [
    ("PIE","*isarno-"),("Proto-Albanian","*hekur-"),("Albanian","hekur"),
  ], [("Gaulish","isarno","iron"),("Welsh","haearn","iron"),("Old Irish","iarn","iron"),("Gothic","eisarn","iron")]),

  ("ar", "gold", "noun", "*h₂eusom-", 0.82, [
    ("PIE","*h₂eusom-"),("Proto-Albanian","*ar-"),("Albanian","ar"),
  ], [("Latin","aurum","gold"),("Lithuanian","áuksas","gold"),("Sanskrit","uṣā","dawn")]),

  ("argjend", "silver", "noun", "*h₂erǵ-", 0.85, [
    ("PIE","*h₂erǵ-"),("Proto-Albanian","*argjend-"),("Albanian","argjend"),
  ], [("Latin","argentum","silver"),("Greek","árgyros","silver"),("Sanskrit","rajata","silver"),("French","argent","silver")]),

  ("bakër", "copper", "noun", "*kypro-", 0.70, [
    ("PIE","*kypro-"),("Proto-Albanian","*bakër-"),("Albanian","bakër"),
  ], [("Latin","cuprum","copper"),("Greek","kypros","Cyprus"),("English","copper","copper")]),

  ("gurë", "stone", "noun", "*gʷreh₂-", 0.88, [
    ("PIE","*gʷreh₂-"),("Proto-Albanian","*gur-"),("Albanian","gurë"),
  ], [("Latin","gravis","heavy"),("Greek","barys","heavy"),("Sanskrit","guru","heavy")]),

  ("miell", "flour", "noun", "*melH-", 0.88, [
    ("PIE","*melH-"),("Proto-Albanian","*miel-"),("Albanian","miell"),
  ], [("Latin","molere","to grind"),("Greek","mýlē","mill"),("English","meal","flour"),("German","Mehl","flour")]),

  ("brumë", "dough", "noun", "*bʰrewH-", 0.80, [
    ("PIE","*bʰrewH-"),("Proto-Albanian","*brum-"),("Albanian","brumë"),
  ], [("Latin","fermentum","ferment"),("German","brauen","to brew"),("English","brew","to brew")]),

  ("enë", "pot, container", "noun", "*h₁en-", 0.78, [
    ("PIE","*h₁en-"),("Proto-Albanian","*en-"),("Albanian","enë"),
  ], [("Latin","unda","wave"),("Sanskrit","und-","to wet")]),

  ("zog", "bird", "noun", "*ǵhow-", 0.72, [
    ("PIE","*ǵhow-"),("Proto-Albanian","*zog-"),("Albanian","zog"),
  ], [("Latin","gallus","rooster"),("Greek","goos","moan")]),

  ("vend", "country, place", "noun", "*wendʰ-", 0.75, [
    ("PIE","*wendʰ-"),("Proto-Albanian","*vend-"),("Albanian","vend"),
  ], [("Latin","endo","in"),("Greek","éndon","within")]),

  ("bregdet", "coast, seashore", "noun", "*bʰregh-deyH-", 0.72, [
    ("PIE","*bʰregh-deyH-"),("Proto-Albanian","*bregdet-"),("Albanian","bregdet"),
  ], [("Latin","ripa","bank"),("Greek","ákra","headland")]),
]

def seed():
    db = SessionLocal()
    try:
        source = db.query(Source).filter_by(name="Orel (1998)").first()
        if not source:
            source = Source(name="Orel (1998)", year=1998, description="Vladimir Orel, Albanian Etymological Dictionary")
            db.add(source)
            db.flush()

        added = 0
        skipped = 0

        for row in DATA:
            word_str, meaning, pos, root, confidence, evo_data, cog_data = row

            existing = db.query(Word).filter_by(word=word_str).first()
            if existing:
                skipped += 1
                continue

            word = Word(word=word_str, normalized=word_str.lower())
            db.add(word)
            db.flush()

            entry = Entry(
                word_id=word.id,
                source_id=source.id,
                meaning=meaning,
                part_of_speech=pos,
                root=root,
                confidence=confidence,
            )
            db.add(entry)
            db.flush()

            for ev in evo_data:
                db.add(Evolution(entry_id=entry.id, stage=ev[0], form=ev[1]))

            for cog in cog_data:
                db.add(Cognate(
                    entry_id=entry.id,
                    language=cog[0],
                    word=cog[1],
                    meaning=cog[2] if len(cog) > 2 else None,
                ))

            added += 1

        db.commit()
        print(f"Done. Added {added} words, skipped {skipped} duplicates.")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed()
