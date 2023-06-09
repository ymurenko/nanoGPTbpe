# -*- coding: utf-8 -*-
import argparse
import json
import os
import re
import unidecode
from concurrent.futures import ProcessPoolExecutor

# for parsing extracted and normalized english wikipedia dumps
# files should be extracted as json and placed into the input directory

parser = argparse.ArgumentParser()
parser.add_argument("input_dir")
parser.add_argument("output_dir")
args = parser.parse_args()

if not os.path.exists(args.output_dir):
    os.makedirs(args.output_dir)

# transliterate most non-latin characters to latin characters
def replace_accents(input_string):
    return unidecode.unidecode(input_string)

# clean out all non-english/latin characters, since they increase the vocabulary size too much
# unidecode doesn't support many of these, and the rest are rare enough that they don't matter
def remove_non_english_chars(text):
    most_asian_chars = r'[\u3000-\u303F\u3040-\u309F\u30A0-\u30FF\u3100-\u312F\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF\uFE30-\uFE4F\uFF00-\uFFEF]'
    all_other_chars = r'[☣☭☯☼♀♂♄♆♋♏♑♒♘♙♟♠♡♣♥♦♭♮♯⚥✓✚❤⟨⟩⨳⬱ⱡⲁⲓⲙⲟⲣⲫⲱⴀⴄⴈⴊⴌⴐⴒⴓⴕⴰⴱⴳⴷⴹⴻⴼⴽⵀⵃⵄⵅⵇⵉⵊⵍⵎⵏⵓⵔⵕⵖⵙⵚⵛⵜⵟⵡⵢⵣⵥⵯ⿰⿱⿺ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ㎡ꙑꙥꙩꙭꙮꜧ꞉ꞌꞯꤷꤼꥁꦏꦑꦒꦔꦗꦠꦡꦢꦣꦩꦪꦫꦮꦯꦲ꧈ꭰꭲꭵꭶꭹꭿꮃꮅꮒꮕꮝꮧꮪꮳꮵꮻꮼꮿꯀꯁꯂꯃꯄꯅꯆꯇꯈꯉꯊꯋꯌꯍꯎꯏꯑꯔꯕꯖꯗꯛꯜꯝꯟꯠꯡꯢ꯱가각간감갑강같개거건걸겠경계고곡곤골곰공과관광괴교구국군굴궁권귀규균근글금기길김까꺄꼼꾼나난날남낮내너널녀년노놀농누늑능니님다단달담답당대더덕덤뎌도독돈동된두둥듀드들등디따때떡똥뜨라락란람랑래랙량럼렁레려령례로룡루르른를름리림립릿마막만말망매맥맹머먹먼멈메면명모목몽묘무묵문물뭏미민믿밀바박반발밤밥방배백버번벌범베변별병보복본볼봉부북분불브븐블비빛빠뻐뽀사산삼상새생샤서석선설성세션소속손송쇼수숙순술슈슐스슬슴습승시식신실심십싸쌈쌍썬쓰씨씽아안알암앙애앤야약양어억언얼엄었에엑엔여역연열영예오옥온옷옹와완왕왜외요용우운울웅워원월위윙유육윤율융으은을음응의이익인일임자잖잘장재쟁저전절점접젓정제조족종좋좌주죽준중즈지직진징짜쪽찌차찬찰참창채책처천철첩첫청쳐초촌총최추춘출춰츄치칠침카칵캐컨컴켜코콜콤쿵퀴크타탁탄탈탕태택탱터테텐토통투트특티틴팅파판패퍼페펙편평폐포푸풍프플피필핑하학한할합항해했향허헌헤혁현협형혜호홀홉홍화환황회횡효후훈훗훼휘휴흠흥희ﬁﷲﷺ﹔ﺍﺎﺏﺒﺠﺤﺩﺪﺮﺴﺷﻀﻁﻋﻓﻙﻞﻟﻠﻣﻨﻩﻫﻮﻲ￼�𐤁𐤂𐤋𐨐𐨤𐨪𐬀𐬌𐬨𐬫𑆑𑆫𑆯𑐣𑐰𒃶𒄩𒈛𒈣𒈨𝄆𝄇𝄫𞤢𞤣𞤤𞤥𞤪𞤫𞤭𞤲🇪🇸ᑦᒡᒪᓂᓄᓗᔨᔭᖃᖏᗸᘅ ᚁᚂᚃᚄᚅᚆᚇᚈᚉᚊᚋᚌᚍᚎᚏᚐᚑᚒᚓᚔᚕᚖᚗᚘᚙᚚ᚛᚜ᚠᚢᚦᚨᚱᚲᚾᛖᛟᜅᜇᜈᜉᜎᜑᝢᝤᝨᝫᝬᝮᝰកខគងចជញឌណតទនបពភមយរលសអឧ០១២៣៤៥៦៧៨៩ᱚᱞᱠᱤᱪᴖᴥآأؤإئابةتثجحخدذرزسشصضطظعغـفقكلمنهوىي١٢٤٥٦٧٨٩ٱٲٹٽپٿڄڅچڇڈڊڌڑڕژښڠڤکڬڭگڵںڻھہۆۇیێېےە۞ۥ۶۷܀ܐܒܓܕܗܘܙܚܛܝܟܠܡܢܣܥܦܨܩܪܫܬݢݣހށނރބކއވމފދތލގސޑޒޔޖޙޛޝޞޢޣޤߊߌߏߖߛߝߞߟߡߣअआइईउऊऋएओकखगघङचछजझञटठडणतथदधनपफबभमयरलळवशषसहऽ।॥०१२३६অআইঈউঊঋএঐওঔকখগঘঙচছজঝঞটঠডঢণতথদধনপফবভমযরলশষসহৎৰৱ৳ਅਈਔਕਖਘਚਜਟਣਤਦਨਪਫਬਮਰਲਵਸਹੜઈકગચછજઝટડતદનપબમયરલવશଇକଙଜଟତଦନମରଲଶସହୟஃஅஇஉஊஐகஙசஜஞடணதநனபமயரறலளழவఅఆఇఈఉఊఋఎఏఐఒఓఔకఖగఘఙచఛజఝఞటఠడఢణతథదధనపఫబభమయరఱలళవశషసహౠ౦౧౨౩౪౫౬౭౮౯ಕಗಜಟಡಣತನಪಬಭಮಯರಲಳವಶಸಹഅഇഉഐകഗങചജടണതദനപഭമയരറലളവശഷസഹൻർൽඅආඑකගජඤඥටඩණතදධනපබභමයරලවශෂසහกขคงจฉชซญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรฤลวศษสหฬอฯะาำเแโใไ๏ກຄງຊຍດທນບຜພມລວສຫອຮະາຳເແໃໄ་།ཀཁགངཆཏཐདནཔཕབམཙཞཡརལསཧကခဂဃငစဆဈဉညဋဌဍဎဏတထဒဓနပဖဗဘမရလဝသဠ၀၁၂၃၄၅၆၇၈၉ၐၑაბგდევზთიკლმნოპჟრსტუფქღყშჩცძწჭხჯჰሀሁህለሊላልሎሐሓሔሕመማምሠረሪራርሮሰሱሳሴስቀቂቃቅበቡቢባብተታቴትቸኀነናንኖኛአኢኣከኩክኮወዊውዎዐዕዘዝየያይዮደዳዴድጃገጌግጎጠጦጰጵጸፀፈፍ¡¢£¤¥§¨©ª«¬­®¯°±²³´µ¶·¸¹º»¼½¾¿×ßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿāăąćĉċčďđēĕėęěĝğġģĥħĩīĭįıĵķĺļľłńņňŉŋōŏőœŕŗřśŝşšţťŧũūŭůűųŵŷźżžſƌƒơưƿǁǂǃǎǐǒǔǚǝǣǧǩǫǭǰǹǿșțȝȟȷɂɐɑɒɓɔɕɖɗɘəɛɜɝɟɠɡɣɤɥɦɧɨɪɫɬɮɯɲɳɵɶɸɹɺɾʀʁʂʃʄʇʈʊʋʌʎʏʐʑʒʔʕʘʛʤʦʧʰʱʲʳʷʸʹʻʼʽʾʿˀˁˆˇˈˊˋˌː˚˜˝ˡˣˤ˥˧˨˩˹˺̇άέήίαβγδεζηθικλμνξοπρςστυφχψωϊόύώϕϛϝϟϡϲϸϻабвгдежзийклмнопрстуфхцчшщъыьэюяѐёђѓєѕіїјљњћќѝўџѡѣѧѫѯѱѳҁҍҏґғқҡҧҫүұҷҹӆӈӏӑӗәӣӧөӱӳԁԙԝաբգդեզէըթժիլխծկհձղճմյնշոչպջռսվտրցւփքօֆև־אבגדהוזחטיךכלםמןנסעףפץצקרשתװ״،ءፐᐃᐅᐯᐸᑐᑕᵛᶻḇḋḍḏḓḗḡḥḩḫḭḱḳḵḷḻḽḿṁṃṅṇṉṋṓṗṙṛṟṣṧṫṭṯṱṿẁẋẏẓẕạảấầẩậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởợụủứừửữựỳỹἀἁἄἅἐἑἔἕἠἡἥἰἱἴἶἷὀὁὄὅὐὑὔὕὖὠὤὦὰὴὶὸᾀᾱᾶῆ῏ῑῖῥῦῴῶ​‌‍‎‏‐‑‒–—―‖‘’‚“”„†‡•…‧ ‬‭ ‰′″›※‽‾‿⁄⁊⁠⁣⁴⁶⁻ⁿ₂₃ₚ₡₣₤₦₩₪₫€₱₵₹₺₽₿℃℅ℓℕ№ℚℜℝ℞℠™ℰ⅓⅔⅕⅛⅜⅝⅟ⅰⅱ←↑→↵⇔∀∂∃∆∇∈∉−∗∘√∛∝∞∪∫∴∼≈≒≔≠≡≤≥⊂⊃⊆⊇⊙⋅⌀⌂⌬⏣④ⓒⓢ─▁◊○●◦☃★☆☊☌☍🐓😊😎🤷􏿾]'
    return re.sub(all_other_chars, '', re.sub(most_asian_chars, '', text))

# need to all floating punctuation marks
# e.g. " ; ; " " , "
def remove_floating_punctuation(text):
    pattern = r'(?<=\s)[,.;:]+(?=\s)'
    return re.sub(pattern, '', text)

# remove all braces and their contents if they don't contain any letters 
# e.g. (         ) () (,  ) (.   ,*!@#$%^&*)
def remove_empty_braces(text):
    pattern = r'\((?:[^\w\s\n]|[ \t])*\)'
    return re.sub(pattern, '', text)

# after removing chars, there will be double spaces all over the place
# removes double-newlines as well so use [] instead of \s if you want to keep newlines
def remove_double_spaces(text):
    pattern = r'\s{2,}'
    return re.sub(pattern, ' ', text)

# parses the json from a wikidump file, and writes the text to a new file
def process_json_files(file):
    print(f"Processing file: {file}")
    input_file_path = os.path.join(args.input_dir, file)

    output_file_name = f"{file}.txt"
    output_file_path = os.path.join(args.output_dir, output_file_name)

    try:
        with open(input_file_path, "r", encoding="utf-8", errors="ignore") as input_file:
            with open(output_file_path, "wb") as output_file:
                for line in input_file:
                    data = json.loads(line)
                    new_text = ''
                    for char in data["text"]:
                        new_text += char
                    replaced_accents = replace_accents(new_text)
                    remvoed_non_english_chars = remove_non_english_chars(replaced_accents)
                    removed_brace_commas = remove_floating_punctuation(remvoed_non_english_chars)
                    removed_empty_braces = remove_empty_braces(removed_brace_commas)
                    removed_double_spaces = remove_double_spaces(removed_empty_braces)
                    output_file.write(removed_double_spaces.encode("utf-8"))
    except Exception as e:
        print(f"Error processing file {file}: {e}")

if __name__ == "__main__":
    with ProcessPoolExecutor() as executor:
        executor.map(process_json_files, os.listdir(args.input_dir))
