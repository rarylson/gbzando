Title: Programas com comportamento aleatório: Introdução (parte 1)
Date: 2014-04-11 00:55
Tags: c, python, programação, aleatoriedade
Slug: programas-comportamento-aleatorio
Category: Programação
Author: Rarylson Freitas
Summary: Neste artigo, iremos mostrar como implementar programas probabilísticos simples nas linguagens C e Python. Além disso, iremos implementar um programa que levanta estatísticas de execução, permitindo, assim, testar nossos programas aleatórios. 

Softwares com comportamento aleatório são usados em simuladores, jogos, algoritmos criptográficos, algoritmos de rede, dentre outras aplicações. Devido a importância destes (em especial em segurança da informação), várias bibliotecas foram desenvolvidas e vários algoritmos de geração de números aleatórios surgiram.

Neste artigo, faremos uma introdução ao uso da aleatoriedade no desenvolvimento de programas.

Inicialmente, iremos apresentar um programa em C que utiliza conceitos básicos de probabilidade para simular o comportamento de um sistema real. Depois, iremos reescrever este programa em Python.

Por fim, iremos desenvolver um programa para levantar estatísticas de execução. O objetivo é testar se os nossos programas aleatórios funcionam conforme esperado.

Simulando um comportamento aleatório em C
-----------------------------------------

Iremos implementar um programa para simular alguns comportamentos comuns de programas reais: tempo de execução e probabilidade de falha. Em outras palavras, iremos desenvolver um programa que ora executa mais rápido, ora mais lento, ora funciona, e ora retorna erro.

Embora simples, nosso programa representa uma aplicação muito útil do uso da aleatoriedade em programação: a realização de simulações.

Iremos chamar nosso programa de **maybe\_it\_works.c:**

    #!c
    #include <stdio.h>
    #include <stdlib.h>
    #include <math.h>
    #include <time.h>    

    #define MIN_EXECUTION_TIME 1
    #define MAX_EXECUTION_TIME 4
    #define PROBABILITY_FAILURE 1
    #define PROBABILITY_RUNS 4

    int main(int argc, char *argv[]) {
        // random vars to simulate real conditions
        int execution_time = 0;
        int return_status = 0;

        float probability = 0;
        float rand_float = 0;

        srand(time(NULL)); // init rand with a pseudorandom seed

        // generate execution time: MIN_EXECUTION_TIME <= execution_time <= MAX_EXECUTION_TIME
        execution_time = (rand() % (MAX_EXECUTION_TIME - MIN_EXECUTION_TIME + 1)) +
                MIN_EXECUTION_TIME;
        // generate return status
        probability = (float)(PROBABILITY_FAILURE) / PROBABILITY_RUNS;
        rand_float = (float)(rand()) / RAND_MAX; // random number in [0,1]
        if (rand_float <= probability) {
            return_status = EXIT_FAILURE;
        } else {
            return_status = EXIT_SUCCESS;
        }   

        // simulate the program execution time 
        sleep(execution_time);
        // simulate a program which sometimes fails
        return return_status;
    }

O programa acima utiliza a função [`rand`](http://www.cplusplus.com/reference/cstdlib/rand/) para gerar números aleatórios. Esta função retorna um inteiro no intervalo entre 0 e `RAND_MAX` e, de forma geral, sempre retorna valores com igual probabilidade de ocorrência.

Utilizamos a função `sleep` para simular o tempo de execução do programa. Uma execução do programa demorará, aproximadamente, um valor inteiro contido no intervalo fechado entre `MIN_EXECUTION_TIME` e `MAX_EXECUTION_TIME`. No nosso caso, entre 1 e 4 segundos.

De forma semelhante, para simular a probabilidade de falha do programa, retornamos falha (`EXIT_FAILURE`) com probabilidade `PROBABILITY_FAILURE / PROBABILITY_RUNS`. No nosso caso, 25% (1/4).

Vamos, agora, compilar e testar nosso programa:

    :::console
    $ gcc -o maybe_it_works maybe_it_works.c
    $ ./maybe_it_works
    $ echo $?
    0

A instrução `echo $?` imprime o código de retorno do último comando executado. No teste realizado, **maybe_it_works** retornou 0. Porém, é importante lembrar que ele poderia ter retornado um valor diferente de zero com probabilidade 25%.

Vamos, agora, utilizar o comando **`time`** para testar melhor nosso programa.

**Obs:** Alguns _shells_ possuem incorporado (_buitin_) uma versão simplificada do comando _time_ (um exemplo é o _shell_ **bash**, padrão em muitas distribuições Linux e no MacOS). Neste caso, para executar o programa _time_ que desejamos apresentar (e não a versão _builtin_), é necessário passar o path completo do programa (conforme explicado em [Why `/usr/bin/time`? (Instead of just `time`)](http://www.thegeekstuff.com/2012/01/time-command-examples/)).

    :::console
    $ /usr/bin/time --quiet -f "time: %E\nexit: %x" ./maybe_it_works
    time: 0:04.00
    exit: 0
    $ /usr/bin/time --quiet -f "time: %E\nexit: %x" ./maybe_it_works
    time: 0:03.00
    exit: 1

### Um pouco sobre sementes (_seeds_)

A função `rand`, na realidade, não retorna um número realmente aleatório. Esta função (e muitas outras semelhantes) retorna um número pseudo-aleatório. Em outras palavras, `rand` é um [gerador de números pseudo-aleatórios](http://en.wikipedia.org/wiki/Pseudorandom_number_generator). 

Este tipo de função gera uma sequência de números que possui propriedades semelhantes às de uma distribuição realmente aleatória. Nestas funções, um conjunto de valores iniciais (chamado de semente, ou _seed_) é utilizado como base para a geração dos novos valores.

Observe que a semente utilizada determina unicamente toda a sequência gerada pelo algoritmo. Isto tem um lado bom e um ruim:

- **Vantagem:** É mais fácil testar e depurar programas, pois podemos utilizar sempre a mesma semente para ter um comportamente previsível para o programa. 
- **Desvantagem:** Descobrir o valor da semente equivale a saber como o programa irá se comportar daquele ponto em diante (algumas pessoas adorariam descobrir as sementes utilizadas nas máquinas existentes nos cassinos de Las Vegas :O ).

Como o nosso programa utiliza o tempo atual, em segundos, para alimentar a semente, dois processos executados no mesmo instante (mesmo segundo) apresentarão o mesmo comportamento (mesmo tempo de execução e mesmo retorno).

O exemplo abaixo mostra essa limitação:

    :::console
    $ # exec 10 times, redirecting each output to a separeted file
    $ for i in {1..10}; do \
    $     ( /usr/bin/time --quiet -f "time: %E\nexit: %x" ./maybe_it_works & ) 2>$i.log; done
    $ # print all logs
    $ cat *.log
    time: 0:01.01
    exit: 1
    time: 0:01.00
    exit: 1
    time: 0:01.03
    exit: 1
    [...]

Neste exemplo, todas as execuções possuíram o mesmo comportamento (tempos de processamento e retornos sempre iguais).

Com certeza, existem implementações melhores que a nossa :(.

Simulando um comportamento aleatório em Python
----------------------------------------------

Vamos, agora, reimplementar o nosso programa em Python.

Python é uma linguagem de alto nível, relativamente moderna, procedural (mas que permite o uso de orientação de objetos), madura, com vários recursos interessantes, porém muito simples.  

O programa **maybe\_it\_works.py** possuirá o nosso código:

    #!python
    #!/usr/bin/env python

    import random
    import time
    import sys 
    
    MIN_EXECUTION_TIME = 1 
    MAX_EXECUTION_TIME = 4 
    PROBABILITY = 1.0 / 4.0 
    SUCCESS = 0 
    FAILURE = 1 
    
    def run_randomly():
        # Generate execution time: MIN_EXECUTION_TIME <= execution_time <= MAX_EXECUTION_TIME
        execution_time = random.randint(MIN_EXECUTION_TIME, MAX_EXECUTION_TIME)
        # Generate return status: random[0,1) < PROBABILITY => FAILURE
        if random.random() < PROBABILITY:
            return_status = FAILURE
        else:
            return_status = SUCCESS
        # Simulate the program execution time
        time.sleep(execution_time)
        # Simulate a program which sometimes fails
        sys.exit(return_status)
     
    if __name__ == "__main__":
        run_randomly()

Primeiramente, em Python, nosso programa não precisou ser compilado e possuiu menos linhas de código.

Entretanto, o mais interessante é o [módulo `random`](https://docs.python.org/2/library/random.html), que possui algumas características e recursos muito úteis que simplificaram a programação do nosso algoritmo aleatório:

- Não é necessário definir uma semente. O módulo `random` [faz isso automaticamente para a gente no momento em que é carregado](https://docs.python.org/2/library/random.html#random.seed). Além disso, este módulo busca uma fonte de aleatoriedade no sistema operacional visando gerar sementes de forma mais inteligente. Somente se o sistema operacional não possuir este mecanismo é que este módulo usará o tempo atual do sistema;
    - Como o sistema operacional em que executamos a experiência possui esta fonte de aleatoriedade, o nosso programa não possuirá a limitação do nosso programa em C, que retornava sempre os mesmos resultados quando vários programas eram executados no mesmo segundo;
    - Caso o programador deseje explicitar a semente a ser utilizada (por exemplo, para facilitar testes e depurar erros), não há problemas: basta utilizar a função `random.seed`;
- É fácil gerar números aleatórios nos intervalos que queremos;
    - Para gerar o tempo de execução, utilizamos a função `random.randint`, que gera números aleatórios inteiros no intervalo que queremos;
    - Para gerar números aleatórios ponto flutuantes, utilizamos a função `random.random`, que gera números no intervalo [0, 1);
        - Caso desejássemos gerar números ponto flutuantes em um intervalo qualquer, a função `random.uniform` poderia ser utilizada.

Para testar o nosso programa em Python, podemos ou executá-lo com o interpretador do Python (`python maybe_it_works.py`) ou simplesmente dar permição de execução ao nosso programa e executá-lo normalmente (a primeira linha do nosso programa indica qual interpretador queremos que seja utilizado). Vamos utilizar a segunda opção:

    :::console
    $ chmod +x maybe_it_works.py
    $ /usr/bin/time --quiet -f "time: %E\nexit: %x" ./maybe_it_works.py
    time: 0:03.05
    exit: 0

Testanto comportamentos aleatórios em Python
--------------------------------------------

Algoritmos aleatórios são um pouco difíceis de testar. Para tornar esta tarefa possível, pode-se criar casos de testes usando sementes previamente definidas, conforme apresentado na sessão anterior.

Entretanto, isso não mostra se, estatisticamente, o comportamento do nosso programa segue a distribuição de probabilidade que escolhemos. Um forma simples de realizar esta verificação seria rodar o nosso programa inúmeras vezes, gerando uma estatística de execução e verificando se ela corresponde ao resultado esperado.

Para este fim, criamos o programa **statistics.py**:

    #!python
    #!/usr/bin/env python
    
    import subprocess
    import time
    
    CHILD_COMMAND = "/usr/bin/env python maybe_it_works.py"
    NUMBER_OF_TESTS = 500 
    
    def statistics():
        # Lists with execution history
        time_history = []
        return_history = []
    
        # Collect statistics
        for i in range(0, NUMBER_OF_TESTS):
            start_time = time.time()
            return_code = subprocess.call(CHILD_COMMAND.split(" "))
            execution_time = time.time() - start_time
            # Update history
            # Round execution_time before update the list. Example: 1.03s to 1s
            time_history.append( round(execution_time) )
            return_history.append(return_code)
        # Count items, dividing them by the total
        # Example: [1, 2, 2] -> {'1': 0.33, '2': 0.66}
        # Based in this code: http://stackoverflow.com/a/9604768/2530295
        counter_time = dict([(i, float(time_history.count(i)) / len(time_history)) 
                for i in set(time_history)])
        counter_return = dict([(i, float(return_history.count(i)) / len(return_history)) 
                for i in set(return_history)])
        # Print statistics
        print "Execution time:"
        print "Time\t\tPercent"
        for key, value in counter_time.iteritems():
            print "{}s\t\t{}%".format(key, value * 100)
        print "\nReturn code:"
        print "Code\t\tPercent"
        for key, value in counter_return.iteritems():
            print "{}\t\t{}%".format(key, value * 100)

    if __name__ == "__main__":
        statistics()

O programa acima irá executar 500 testes em sequência. Em cada teste, ele irá executar **maybe_it_works.py**, calculando o seu tempo de execução e obtendo o retorno do programa.

Para calcular o tempo de execução, utilizamos duas vezes a função `time.time` (uma antes e outra depois da execução do teste) e calculamos a diferença entre os valores obtidos. De posse desse valor, fazemos um arredondamento para poder agrupar tempos de execução próximos.

Já o retorno da execução de um teste é obtido através do módulo `subprocess`, muito útil para execução de comandos no sistema operacional. Sua [função `subprocess.call`](https://docs.python.org/2/library/subprocess.html#subprocess.call) recebe como parâmetro uma lista de argumentos a serem passados à interface de comandos do sistema operacional. Ao receber esta lista de argumentos, a função irá realizar as operações necessárias de _escape_ e _quoting_ antes de passá-los ao _shell_ sistema operacional. Essa função irá esperar sincronamente pela execução do comando e, em seguida, irá retornar o código de retorno deste.

**Obs:** É possível passar todos os parâmetros através de uma única _string_ (utilizando o parâmetro `shell=True`). Entretanto, [essa utilização é desencorajada, visto que pode deixar o programa vulnerável a ataques de _shell injection_](https://docs.python.org/2/library/subprocess.html#frequently-used-arguments).

Depois de obter nossas métricas (tempo de execução e retorno), nós as inserimos em listas apropriadas. No momento seguinte, contamos quanto cada valor aparece na lista, dividindo esta contagem pelo número total de elementos.

Logo depois, geramos um dicionário ou _dict_ (em outras linguagens chamado de _map_ ou _hashtable_). Este dicionário irá possuir como chave os valores das nossas listas (o número de segundos, ou o código de retorno), e como valor a frequência relativa com que um dado valor aparece na nossa lista original.

A linha 24 do nosso programa possui um exemplo esclarecedor: o nosso código transformaria a lista `[1, 2, 2]` no dicionário `{'1': 0.33, '2': 0.66}`.

Por fim, iteramos sobre os nossos dicionários e imprimimos as estatisticas coletadas na tela.

Vamos, agora, testar o nosso programa:

    :::console
    $ chmod +x statistics.py
    $ ./ statistics.py
    Execution time:
    Time        Percent
    1.0s        24.2%
    2.0s        26.2%
    3.0s        23.0%
    4.0s        26.6%
    
    Return code:
    Code        Percent
    0           78.6%
    1           21.4%

No teste acima, obvervamos que os valores retornados estão próximos do esperado: próximo a 25% para os tempos de execução, e próximo a 25% para o número de falhas.

Referências
-----------

- [Wikipedia - Pseudorandom number generator](http://en.wikipedia.org/wiki/Pseudorandom_number_generator)
- [rand - C++ Reference](http://www.cplusplus.com/reference/cstdlib/rand/)
- [srand - C++ Reference](http://www.cplusplus.com/reference/cstdlib/srand/)
- [Python - Tutorial](https://docs.python.org/2/tutorial/index.html)
