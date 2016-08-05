Title: Programas com comportamento aleatório: Números pseudo-aleatórios e aleatórios verdadeiros (parte 2)
Date: 2015-09-27 19:39
Tags: c, python, programação, aleatoriedade
Slug: programas-comportamento-aleatorio-2
Category: Programação
Author: Rarylson Freitas
Summary: Neste artigo, vamos mostrar o que são sementes (seeds) e como elas são usadas na geração de números pseudo-aleatórios. Vamos também mostrar sua importância e como elas estão relacionadas à segurança de uma aplicação.

No artigo [Programas com comportamento aleatório: Introdução (parte 1)]({filename}programas-comportamento-aleatorio.md), mostramos como construir programas simples com comportamento aleatório. Além disso, mostramos um exemplo de como podemos verificá-los, para ver se os resultados que eles geram estão dentro do esperado.

Também falamos um pouquinho sobre sementes (_seeds_). Mas bem pouquinho mesmo...

Neste artigo, vamos nos concentrar nesse assunto: sementes. Vamos mostrar o que são sementes (seeds) e como elas são usadas na geração de números pseudo-aleatórios. Vamos também mostrar sua importância e como elas estão relacionadas à segurança de uma aplicação.

Além disso, vamos falar sobre os números aleatórios verdadeiros e apresentar técnicas de se obtê-los.

Sementes (_seeds_) e números pseudo-aleatórios
----------------------------------------------

A imensa das funções de aleatoriedade, na realidade, não geram números realmente aleatórios. Elas [geram números **pseudo-aleatórios**](https://en.wikipedia.org/wiki/Pseudorandom_number_generator). De forma simplificada, elas são inicializadas com um número inicial, que chamamos de **semente ou _seed_**. Então, elas usam estes números para gerar os demais.

É importante perceber que, embora os números gerados não sejam realmente aleatórios, cada uma dessas funções gera sequências de números que possuem propriedades semelhantes às de uma distribuição realmente aleatória.

Para dar um exemplo, vamos implementar em C um [gerador congruencial linear](https://en.wikipedia.org/wiki/Linear_congruential_generator) (_Linear Congruential Generator_, ou LCG), que é uma classe de geradores de números pseudo-aleatórios bem simples.

Para isso, vamos criar o arquivo `lcg.c` com o seguinte código:

```
#!c
#define LCG_A 501
#define LCG_C 77
#define LCG_M 32

static unsigned int current_seed = 0;

// update the seed
void lcg_seed(unsigned int seed) {
    current_seed = seed;
}

// generate a random number using a linear congruential generator
unsigned int lcg_rand(void) {
    // cast the multiplication to 'long unsigned int' to avoid overflows
    current_seed = ((long unsigned int)(LCG_A * current_seed) + LCG_C) % LCG_M;
    return current_seed;
}
```

E o seu respectivo header `lcg.h`:

```
#!c
#ifndef LCG_H
#define LCG_H
void lcg_seed(unsigned int seed);
unsigned int lcg_rand(void);
#endif
```

Dando um pouco de base matemática, um LCG gera números através da função:

\` x_n = ( ax_(n-1) + c ) mod m \`
{: .center }

A semente, ou _seed_, é usada para iniciar a sequência (\` x_0 \`).

Criamos duas funções, uma para inicializar a semente (`lcg_seed`), e outra para gerar os números aleatórios (`lcg_rand`).

Os parâmetros `LCG_A`, `LCG_C` e `LCG_M` foram escolhidos seguindo algumas propriedades matemáticas para [garantir uma boa performance](https://en.wikipedia.org/wiki/Linear_congruential_generator#Parameters_in_common_use) (módulos de base 2 são mais rápidos de se calcular) e [garantir período completo](https://en.wikipedia.org/wiki/Linear_congruential_generator#Period_length) (gerar todos os números possíveis antes de começar a repetir a sequência).

Vamos, então, fazer um programinha (`lcg_test.c`) para testar as nossas funções:

```
#!c
#include <stdio.h>
#include "lcg.h"

#define SEEDS 3
#define SEED_1 3
#define SEED_2 7
#define SEED_3 9
#define NUMS 20

int main(int argc, char *argv[]) {
    int seeds[SEEDS] = {SEED_1, SEED_2, SEED_3};
    int i = 0;
    int j = 0;

    for (i = 0; i < SEEDS; i++) {
        lcg_seed(seeds[i]);
        printf("Random numbers (seed %d): ", seeds[i]);
        for (j = 0; j < NUMS; j++) {
            printf("%u", lcg_rand());
            if (j != NUMS -1) {
                printf(", ");
            }
        }
        printf("\n");
    }
}
```

Esse programinha gera 20 números aleatórios para três sementes diferentes.

Vamos então compilar e rodar o nosso programa:

```console
$ gcc -o lcg_test lcg_test.c lcg.c
$ chmod +x lcg_test
$ ./lcg_test
Random numbers (seed 3): 14, 29, 0, 7, 2, 1, 20, 11, 22, 5, 8, 15, 10, 9, 28, 19, 30, 13, 16, 23
Random numbers (seed 7): 2, 1, 20, 11, 22, 5, 8, 15, 10, 9, 28, 19, 30, 13, 16, 23, 18, 17, 4, 27
Random numbers (seed 9): 28, 19, 30, 13, 16, 23, 18, 17, 4, 27, 6, 21, 24, 31, 26, 25, 12, 3, 14, 29
```

Prontinho... De fato, nossas novas funções geram números que se **parecem** ser aleatórios, no intervalo entre 0 e `LCG_M`.

Ah, um detalhe bem legal é que versões mais simples das funções `rand` e `srand` do C são implementadas como LCGs, inclusive a implementação padrão da especificação do C. Mais detalhes são dados [aqui](http://stackoverflow.com/questions/4768180/rand-implementation/4768189#4768189).

Obviamente, se rodarmos o nosso programa várias vezes, ele sempre vai imprimir a mesma coisa: pois a semente é sempre a mesma. Em outras palavras, ao conhecer a semente, nós podemos predizer os números que serão gerados.

Tá legal... Já sabemos o que é um número pseudo-aleatório e o que são sementes. Mas aí você se pergunta:

- Por quê usar números pseudo-aleatórios e sementes? Por quê não simplesmente usar números aleatórios verdadeiros, que sejam completamente imprevisível?
- Se eu usar sempre a mesma semente, os números serão sempre os mesmos e poderemos predizê-los. Isso não é problema de segurança?

Boas perguntas, caro leitor!!!

Primeiramente, obter números aleatórios verdadeiros dá bem mais trabalho e é uma tarefa bem mais lenta do que gerar números pseudo-aleatórios. Assim, performance é uma boa razão para usar números pseudo-aleatórios.

Uma segunda razão é que é poder usar a mesma semente para obter sempre os mesmos resultados é bastante útil para testes e depuração. Imagine-se tentando resolver um bug em um software que a todo momento se comporta de forma diferente, e dá para imaginar a utilidade disso.

E sim: usar sempre a mesma semente em um programa pode gerar vários problemas de segurança. Exceto em situações específicas, não faça isso!

A dica é usar um número aleatório verdadeiro (ou um que chegue perto de ser um aleatório verdadeiro) para iniciar a semente e, à partir de então, usar números pseudo-aleatórios. Uma dica nos casos onde precisemos de mais segurança ainda, reiniciar de tempos em tempos a semente usando um novo número aleatório verdadeiro pode ser uma boa ideia.

### Usando sementes fixas para debugar um programa

Vamos fazer um novo programa de teste, mas usando técnicas um pouco mais inteligentes. Ele irá usar um gerador de números pseudo-aleatórios um pouco melhor (`rand`, da `stdlib`), usará uma semente fixa quando o compilarmos com a flag de debug, e usará sementes que mudam com o tempo quando o compilarmos sem a flag de debug.

Vamos chamá-lo de `smart_seed.c`:

```
#!c
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define DEBUG 0
#define DEBUG_SEED 99
#define NUMS 10
#define NUM_MAX 100

int main(int argc, char *argv[]) {
    int i = 0;

    // if debug, use a well-known seed
    if (DEBUG) {
        srand(DEBUG_SEED);
    // else, use the system time as seed
    } else {
        srand(time(NULL));
    }

    printf("Random numbers: ");
    for (i = 0; i < NUMS; i++) {
        printf("%u", rand() % NUM_MAX);
        if (i != NUMS -1) {
            printf(", ");
        }
    }
    printf("\n");
}
```

Se nós ativarmos e flag de debug:

```diff
-#define DEBUG 0
+#define DEBUG 1
```

O nosso programa irá gerar sempre as mesmas saídas, fazendo que seja mais fácil testá-lo:

```console
$ gcc -o smart_seed smart_seed.c
$ chmod +x smart_seed
$ ./smart_seed
Random numbers: 93, 40, 49, 27, 26, 41, 68, 73, 28, 67
$ ./smart_seed
Random numbers: 93, 40, 49, 27, 26, 41, 68, 73, 28, 67
$ ./smart_seed
Random numbers: 93, 40, 49, 27, 26, 41, 68, 73, 28, 67
```

Já se o compilarmos sem a flag de debug, o seu output mudará com o tempo:

```console
$ gcc -o smart_seed smart_seed.c
$ chmod +x smart_seed
$ ./smart_seed
Random numbers: 90, 72, 91, 51, 6, 30, 56, 77, 57, 48
$ ./smart_seed
Random numbers: 97, 21, 17, 62, 36, 55, 0, 8, 33, 10
$ ./smart_seed
Random numbers: 11, 19, 16, 31, 2, 99, 88, 17, 32, 34
```

Entretanto, se o executarmos várias vezes no mesmo segundo, a chamada `time(NULL)` retornará sempre o mesmo valor, e ele usará sempre a mesma semente, retornando sempre os mesmos números:

```console
$ for i in {1..4}; do ./smart_seed; done
Random numbers: 56, 97, 83, 46, 57, 20, 53, 39, 29, 49
Random numbers: 56, 97, 83, 46, 57, 20, 53, 39, 29, 49
Random numbers: 56, 97, 83, 46, 57, 20, 53, 39, 29, 49
Random numbers: 56, 97, 83, 46, 57, 20, 53, 39, 29, 49
```

Além disso, se um atacante perceber que estamos usando o tempo em segundos como gerador de sementes, isso pode comprometer nossa segurança.

Esse é o mesmo problema que existe no programa `maybe_it_works.c`, apresentado [no nosso artigo anterior (parte 1)]({filename}programas-comportamento-aleatorio.md).

A verdade é que `time(NULL)` não nos retorna um número aleatório verdadeiro e difícil de predizer, e ele é um método ruim para gerar sementes em aplicações mais sérias. Para estar aplicações, devemos usar números aleatórios verdadeiros com melhor aleatoriedade.

Números aleatórios verdadeiros
------------------------------

Números aleatórios verdadeiros são diferentes de números pseudo-aleatórios pois não existe um processo determinístico que os geram. Eles são mais difíceis de se conseguir, mas por outro lado são muito menos previsíveis. Eles [possuem suas vantagens e desvantagens](https://en.wikipedia.org/wiki/Random_number_generation#.22True.22_vs._pseudo-random_numbers). 

Vamos fazer uma experiência simples para apresentar conceitos importantes sobre números aleatórios verdadeiros.

Pense em um número. Isso mesmo, pensa aí... Pensou? Parabéns! Você acabou de gerar um número aleatório!

Agora, que número você pensou? Você pensou em algo como 95263634? Ou será que você pensou em um número inteiro simples, pequeno, menor que 1000? Ou será que o número que você pensou está relacionado há algo na sua vida (uma data, um número favorito, dentre outros)? Provavelmente, o número que você gerou, apesar de aleatório, não tem boas propriedades.

Quando queremos um número aleatório verdadeiro, geralmente buscamos um número impossível de se prever e que, ao mesmo tempo, não tenha propriedades que o torne mais fácil de ser adivinhado. Por exemplo, não queremos que exista uma tendência deles caírem numa determinada faixa, como por exemplo serem números que tendem a ser pequenos (geralmente números gerados por humanos são assim), ou que tenham dígitos significativos fáceis de adivinhar (como o relógio do computador) ou mesmo que tendem a ficar em uma faixa contínua (como a temperatura da CPU). Queremos que eles sejam o mais "caótico" possível. Essa medida de impredictibilidade está relacionada a um conceito chamado de **entropia**.

Hoje, existem várias formas de um computador obter números aleatórios verdadeiros. Vamos apresentar algumas dessas técnicas, em ordem crescente de entropia que elas apresentam:

- **Comportamento humano:** Podemos usar as teclas digitadas, os movimentos do ponteiro do mouse, dentre outras ações de um usuário do computador, para gerar números aleatórios;
    - Infelizmente, o usuário do computador não gera dados tão aleatórios assim, mas com um certo tratamento em cima dos dados de entrada, é possível gerar números aleatórios razoáveis;
- **Propriedades físicas:** Podemos usar o tempo, a temperatura de um componente do hardware, o ruído branco captado pelo microfone do computador, o ruído gerado pelo próprio hardware, dentre outras características físicas, para gerar números aleatórios;
    - Os números originais obtidos podem ser ruins (por exemplo, a temperatura da CPU varia em uma faixa conhecida), mas se ficarmos somente com os números menos significativos (por exemplo, extraindo os números depois da vírgula da temperatura da CPU, como a transformação 48,4675 ºC em 4675), podemos obter números aleatórios bem melhores;
- **Propriedades quânticas:** Podemos usar propriedades super legais da Física Quântica, como a posição de uma nanopartícula e propriedades do quantum, para gerar números aleatórios;
    - Um cara aí chamado Heisenberg descobriu um "tal" de [Princípio da Incerteza de Heisenberg](https://en.wikipedia.org/wiki/Uncertainty_principle). Esse princípio (e alguns outros conceitos, como a [entropia de Von Neumann](https://en.wikipedia.org/wiki/Von_Neumann_entropy)) mostram que a Física Quântica é um bom caminho para gerar números aleatórios.

Hoje em dia, algumas bibliotecas e os sistemas operacionais nos fornecem métodos de obter números aleatórios bons e seguros. Vamos mostrar alguns desses métodos ainda neste artigo. Entretanto, é interessante saber que, para quem precisar de aplicações ainda mais seguras, existem [hardwares especiais para gerar números aleatórios](https://en.wikipedia.org/wiki/Hardware_random_number_generator).

### O /dev/random e a entropia no Linux

Uma forma bem consolidada, segura e interessante de se obter números aleatórios com boa entropia no Linux é usando os [dispositivos `/etc/random` e `/dev/urandom`](https://en.wikipedia.org/wiki//dev/random).

O funcionamento do `/etc/random` é apresentado a seguir:

- O kernel do Linux fica continuamente recebendo bits aleatórios gerados pelo usuário e pelo hardware;
- O kernel passa então este valores por um filtro removedor de tendências (chamado de filtro _antibias_) e depois os usa para alimentar o seu _entropy pool_;
- Ao alimentar o pool com novos valores, o kernel calcula sua entropia total (`entropy_avail`);
- O Kernel então disponibiliza no _device_ `/dev/random` números pseudo-aleatórios gerados à partir deste pool;
- Sempre que o pool é alterado, sua entropia é recalculada;
    - Quando novos números chegam ao pool, o valor de `entropy_avail` aumenta;
    - Por outro lado, sempre que algum programa consome valores de `/dev/random`, o valor de `entropy_avail` diminui;
- Quando o _entropy pool_ está com baixa entropia, o `/dev/random` deixa de gerar números pseudo-aleatórios e fica aguardando pela chegada de novos valores aleatórios, até que a entropia do sistema volte a ficar boa e que novos números pseudo-aleatórios possam ser gerados por novas sementes de alta entropia.

Esse esquema todo é lindo e funcional, se não fosse por um problema: leituras ao `/dev/random` pode ser bloqueantes. Isso é, um programa pode ficar esperando um tempo indefinido até que o `/dev/random` torne a gerar números aleatórios.

Uma solução é usar o dispositivo `/dev/urandom` (_unlimited random_). Este dispositivo é semelhante ao random, mas ele pode reutilizar números aleatórios do pool de entropia para gerar números pseudo-aleatórios (sem consumir, assim, a entropia do sistema).

O `/dev/urandom` é uma forma performática e segura de se obter números aleatórios. Entretanto, como um número aleatório gerado pode estar de alguma forma relacionado à números anteriores (quando o pool está com baixa entropia), em casos específicos onde se requer um alto grau de segurança, recomenda-se usar o `/dev/random`.

Vamos, agora, fazer alguns testes com o `/dev/random`:

```console
$ cat /proc/sys/kernel/random/entropy_avail
1013
$ time head -c 100 /dev/random > /dev/null
real    0m0.002s
[...]
$ cat /proc/sys/kernel/random/entropy_avail
502
$ time head -c 100 /dev/random > /dev/null
real    0m5.660s
[...]
$ cat /proc/sys/kernel/random/entropy_avail
180
$ time head -c 100 /dev/random > /dev/null
real    0m8.616s
[...]
```

Nos nossos testes, ficou nítido que baixos valores de entropia (`/proc/sys/kernel/random/entropy_avail`) podem fazer com que o `/dev/random` fique bloqueante.

Agora, vamos repetir a mesma experiência usando o `/dev/urandom`:

```console
$ time head -c 100 /dev/urandom > /dev/null
real    0m0.002s
[...]
$ cat /proc/sys/kernel/random/entropy_avail
1344
$ time head -c 100 /dev/urandom > /dev/null
real    0m0.002s
[...]
```

Bem mais rápido!

E mesmo que usemos o `/dev/random` para reduzir a entropia do sistema, o `/dev/urandom` continua sendo rápido e não bloqueante:

```console
$ head -c 1000 /dev/random > /dev/null
$ cat /proc/sys/kernel/random/entropy_avail
130
$ time head -c 1000 /dev/urandom > /dev/null
real    0m0.002s
[...]
```

Isso responde a [pergunta desse cara](http://superuser.com/questions/359599/why-is-my-dev-random-so-slow-when-using-dd), que queria saber porque criar arquivos aleatórios usando o `/dev/random` era tão lento.

### Gerando boas sementes

Agora, já sabemos várias técnicas para gerar sementes melhores que usando `time(NULL)`.

Assim, vamos reescrever o nosso programa para que ele gere melhores sementes. Vamos adotar a técnica de usar o `/dev/urandom` para este fim.

Vamos chamá-lo agora de `better_smart_seed.c`:

```
#!c
#include <stdio.h>
#include <stdlib.h>

#define DEBUG 0
#define DEBUG_SEED 99
#define NUMS 10
#define NUM_MAX 100

// returns a random number from /dev/urandom
// based on: http://stackoverflow.com/a/11990066/2530295
unsigned long int get_urandom(void) {
    unsigned long int urandom = 0;
    FILE *f = NULL;

    // open /dev/urandom
    if (! (f = fopen("/dev/urandom", "r"))) {
        printf("Error while opening /dev/urandom\n");
    }
    // read an 'unsigned long int' from /dev/urandom
    fread((char*)(&urandom), sizeof(urandom), 1, f);
    fclose(f);

    return urandom;
}

int main(int argc, char *argv[]) {
    int i = 0;

    // if debug, use a well-known seed
    if (DEBUG) {
        srand(DEBUG_SEED);
    // else, use a good seed
    } else {
        srand(get_urandom());
    }

    printf("Random numbers: ");
    for (i = 0; i < NUMS; i++) {
        printf("%u", rand() % NUM_MAX);
        if (i != NUMS -1) {
            printf(", ");
        }
    }
    printf("\n");
}
```

Primeiro, nós criamos a função `get_urandom`, que retorna um valor aleatório obtido de `/dev/urandom`.

Depois, nós retiramos a bibliota `time.h` das nossas inclusões:

```diff
- #include <time.h>
```

Por fim, nós modificamos a linha 34 para usar a nossa nossa função em vez do tempo do sistema na hora de gerar nossa semente:

```diff
-         srand(time(NULL));
+         srand(get_urandom());
```

E agora é só compilar e rodar:

```console
$ gcc -o better_smart_seed better_smart_seed.c
$ chmod +x better_smart_seed
$ for i in {1..4}; do ./better_smart_seed; done
Random numbers: 42, 45, 39, 27, 38, 36, 66, 53, 3, 24
Random numbers: 38, 23, 80, 65, 19, 36, 10, 10, 52, 7
Random numbers: 29, 21, 84, 78, 23, 97, 10, 30, 70, 94
Random numbers: 34, 31, 65, 10, 90, 23, 10, 68, 56, 16
```

E prontinho... Agora temos um programa com comportamento aleatório que usa boas práticas na utilização de sementes.

Referências
-----------

- [Wikipedia - Random Number Generation](https://en.wikipedia.org/wiki/Random_number_generation)
- [Wikipedia - Linear congruential generator](https://en.wikipedia.org/wiki/Linear_congruential_generator)
- [Wikipedia - /dev/random](https://en.wikipedia.org/wiki//dev/random)
