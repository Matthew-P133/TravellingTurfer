def solution(x):
    # Your code here
    return ''.join([parse(letter) for letter in x])
    
def parse(letter):
    alphabet = [
        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i',
        'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 
        's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    if letter in alphabet:
        return alphabet[25-alphabet.index(letter)]
    return letter

print(solution('Yvzs! I xzm\'g yvorvev Lzmxv olhg srh qly zg gsv xlolmb!!'))
