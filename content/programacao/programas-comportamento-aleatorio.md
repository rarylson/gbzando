Title: Programas com comportamento aleatório
Date: 2014-01-26 18:10
Tags: c, python, programação, random
Slug: programas-comportamento-aleatorio
Category: Programação
Author: Rarylson Freitas
Summary: Bla bla
Status: draft

Simulando um comportamento aleatório em C
-----------------------------------------

**maybe\_it\_works.c:**

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

        int return_status_temp = 0;

        srand(time(NULL)); // init rand with a pseudorandom seed

        // generate execution time: MIN_EXECUTION_TIME <= execution_time <= MAX_EXECUTION_TIME
        execution_time = (rand() % (MAX_EXECUTION_TIME - MIN_EXECUTION_TIME + 1)) +
                MIN_EXECUTION_TIME;
        // generate return status
        // 0 <= return_status_temp <= PROBABILITY_RUNS - 1
        return_status_temp = rand() % PROBABILITY_RUNS;
        // return_status_temp < PROBABILITY_FAILURE => failure
        if (return_status_temp < PROBABILITY_FAILURE) {
            return_status = EXIT_FAILURE;
        } else {
            return_status = EXIT_SUCCESS;
        }   

        // simulate the program execution time 
        sleep(execution_time);
        // simulate a program which sometimes fail
        return return_status;
    }

O programa acima utiliza a função [**rand**](http://www.cplusplus.com/reference/cstdlib/rand/) para gerar números aleatórios, tornando o comportamento do programa probabilístico. Esses números são utilizados para simular dois comportamentos típicos de um programa real: tempo de processamento e ocorrência de erros.

Nosso programa utiliza a função **sleep** para simular o tempo de execução do programa. Uma execução do programa demorará, aproximadamente, um valor inteiro contido no intervalo fechado entre `MIN_EXECUTION_TIME` e `MAX_EXECUTION_TIME`. No nosso caso, entre 1 e 4 segundos.

De forma semelhante, para simular a probabilidade de falha do programa, retornamos falha (`EXIT_FAILURE`) com probabilidade `PROBABILITY_FAILURE / PROBABILITY_RUNS`. No nosso caso, 25% (1/4).

Para implementar essa funcionalidade, na linha 25, armazenou-se o valor `rand() % PROBABILITY_RUNS` em uma variável auxiliar. Este valor é um inteiro entre 0 e `PROBABILITY_RUNS - 1`. Assim, cada um dos valores que esta variável pode assumir possui probabilidade `1 / PROBABILITY_RUNS` de ocorrer. Isso implica que esta variável assumirá um valor no intervalo entre 0 e `PROBABILITY_FAILURE - 1` com probabilidade `PROBABILITY_FAILURE / PROBABILITY_RUNS`. O bloco _if/else_ que se inicia na linha 27 utiliza-se deste fato para assossiar `EXIT_FAILURE` a variável `return_status` com probabilidade `PROBABILITY_FAILURE / PROBABILITY_RUNS`.

Agora, vamos compilar e testar nosso programa:

    :::bash
    gcc -o maybe_it_works maybe_it_works.c
    ./maybe_it_works
    echo $?
    > 0

A instrução `echo $?` imprime o código de retorno do último comando executado. No teste realizado, **maybe_it_works** retornou 0. Porém, é importante lembrar que ele poderia ter retornado um valor diferente de zero com probabilidade 25%.

Vamos, agora, utilizar o comando **time** para testar melhor nosso programa.

**Obs:** Alguns _shells_ possuem, incorporado neles (_buitin_), uma versão simplificada do comando _time_ (um exemplo é o _shell_ **bash**, padrão em muitas distribuições Linux e no MacOS). Neste caso, para executar o programa _time_ desejado (e não a versão _builtin_) é necessário passar o path completo do programa (conforme explicado em [Why /usr/bin/time? (Instead of just time)](http://www.thegeekstuff.com/2012/01/time-command-examples/)).

    :::bash
    /usr/bin/time --quiet -f "time: %E\nexit: %x" ./maybe_it_works
    > time: 0:04.00
    > exit: 0
    /usr/bin/time --quiet -f "time: %E\nexit: %x" ./maybe_it_works
    > time: 0:03.00
    > exit: 1

Nosso programa possui uma limitação: ele utiliza o tempo atual, em segundos, para alimentar a semente (_seed_) utilizada para aleatorizar a função _rand_. Com isso, caso dois processos sejam executados no mesmo instante (mesmo segundo), ambos apresentarão o mesmo comportamento (mesmo tempo de execução e mesmo retorno). Isso não será um problema nos nossos exemplos.

**Obs:** Em casos onde isto seja um problema, pode-se utilizar outros métodos de iniciar a semente do _rand_, como o uso da função [_clock\_gettime_](http://linux.die.net/man/3/clock_gettime), ou o uso de um valor aleatório gerado pelo sistema (como o _device file_ [`/dev/random` do Linux](http://en.wikipedia.org/wiki//dev/random), que [pode ser lido para obter uma semente](http://stackoverflow.com/a/11990066/2530295)). 

### Um novo algoritmo

    :::c    
    float probability = 0;
    float rand_float = 0;

a

    :::c
    // generate return status
    probability = (float)PROBABILITY_FAILURE / PROBABILITY_RUNS;
    rand_float = (float)rand() / RAND_MAX; // random number in [0,1)
    if (rand_float < probability) {
        return_status = EXIT_FAILURE;
    } else {
        return_status = EXIT_SUCCESS;
    }

Sobre sementes (_seeds_)
------------------------

-> Porque usar sementes? Qual a vantagem de uma função pseudo-aleatória retornar os mesmos valores?

### Obtendo via linha de comando

    :::c
    // init rand with a seed
    unsigned int seed_int = (unsigned int)time(NULL); // default value
    if (argc > 1) {
        seed_int = (unsigned int)atol(argv[1]); // reading from command line args
    }   
    srand(seed_int);


### Usando o clock do processador

Remover `#include <time.h>`.

    :::c
    // get Time Stamp Counter (TSC) in Pentium (x86 and x64). this may not work 
    // with multiple processors, because there is many TSC (one for each processor)
    unsigned long long int rdtsc(void)
    {
        unsigned long long int x;
        unsigned a, d;
    
        __asm__ volatile("rdtsc" : "=a" (a), "=d" (d)); // exec assemble instruction
        return ((unsigned long long)a) | (((unsigned long long)d) << 32);;
    }

bla

    :::c
    // init rand with the number of cpu clocks
    unsigned long long int clock_ticks = 0;
    clock_ticks = rdtsc();
    srand((unsigned int)clock_ticks);

#### Usando _jiffies_ no Linux

    :::c
    #include <linux/jiffies.h>

bla

    :::c
    srand((unsigned int)jiffies);

Ver: http://www.makelinux.net/ldd3/chp-7-sect-1

### Usando o device `/dev/urandom`

    :::c
    // init rand with the random device (/dev/urandom)
    // not using /dev/random because reading it can be slow
    // based in this code: http://stackoverflow.com/a/11990066/2530295
    unsigned int seed_int = 0;
    FILE *file = NULL;
    if (! (file = fopen("/dev/urandom", "r"))) { // open /dev/urandom
        printf("Error while opening /dev/urandom\n");
    }   
    fread((char*)(&seed_int), sizeof(seed_int), 1, file); // read a random seed
    fclose(file);
    srand(seed_int); // init rand with seed

Simulando um comportamento aleatório em Python
----------------------------------------------

See: http://docs.python.org/2/library/random.html
There is no need to init seed, because "current system time is used"
And "If randomness sources are provided by the operating system, they 
are used instead of the system time"
See: http://docs.python.org/2/library/random.html#random.seed
        
See: http://stackoverflow.com/a/419986/2530295

**maybe\_it\_works.py**:

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
        # Simulate a program which sometimes fail
        sys.exit(return_status)
     
    if __name__ == "__main__":
        run_randomly()
 

Testanto comportamentos aleatórios em Python
--------------------------------------------

**statistics.py**:

    #!python
    #!/usr/bin/env python
    
    import subprocess
    import time
    
    CHILD_COMMAND = "/usr/bin/env python maybe_it_works.py"
    NUMBER_OF_TESTS = 500 
    
    def statistics():
        # Arrays with execution history
        time_history = []
        return_history = []
    
        # Collect statistics
        for i in range(0, NUMBER_OF_TESTS):
            start_time = time.time()
            return_code = subprocess.call(CHILD_COMMAND.split(" "))
            execution_time = time.time() - start_time
            # Update history
            # Round execution_time after update. Example: 1.03s to 1s
            time_history.append( round(execution_time) )
            return_history.append(return_code)
        # Count items, dividing by the total
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

Testando:

    :::bash
    python statistics.py 
    > Execution time:
    > Time        Percent
    > 1.0s        24.2%
    > 2.0s        26.2%
    > 3.0s        23.0%
    > 4.0s        26.6%
    > 
    > Return code:
    > Code        Percent
    > 0           78.6%
    > 1           21.4%

Referências
-----------

TODO Update here

- [Wikipedia - Zombie Process](http://en.wikipedia.org/wiki/Zombie_process)
