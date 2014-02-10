Title: Enviando e tratando sinais em processos Linux
Date: 2013-10-08 19:00
Tags: linux, c, processos, sinais
Slug: processos-sinais
Category: Linux
Author: Rarylson Freitas
Summary: Entenda como funciona a comunicação por sinais (_signals_) em Linux e conheça os sinais mais comuns. Saiba como enviar e tratar o recebimento de sinais. Neste artigo, iremos implementar comunicação usando sinais em C e, ao fim, iremos desenvolver um programa que saberá tratar sinais para realizar as operações stop e reload.

Em um artigo anterior, chamado [Tipos de processos no Linux]({filename}/linux/processos-tipos.md), mostramos como funcionam os diversos tipos de processos e a hierarquia de processos no Linux.

Agora, iremos motrar um outro conceito: a comunição entre processos usando sinais (_signals_).

Iremos realizar diversas experiências para mostrar como podemos enviar e tratar sinais na aplicação. Além disso, iremos desenvolver um programa que saberá realizar as operações _stop_ e _reload_ através do tratamento de sinais.

Sinais no Linux
---------------

Enviar sinais ([_signals_](http://en.wikipedia.org/wiki/Unix_signal)) é uma forma simples de comunicação entre processos utilizada no Linux (e outros sistemas _Unix like_). É um tipo de comunicação assíncrona e baseada em eventos.

De forma simplificada, um processo envia um sinal para outro processo e este, ao receber o sinal, terá sua linha de execução interrompida e irá executar o _handler_ daquele sinal. Logo após, o processo retornará ao ponto em que foi interrompido, continuando sua linha de execução.

Existem diversos tipos de sinais, cada um apropriado para um certo tipo de evento: no [artigo passado]({filename}/linux/processos-tipos.md), foram apresentados sinais para parar a execução, para pausar um processo, e para resumir um processo.

Cada sinal possui um comportamento _default_ definido pelo sistema operacional. A maioria destes comportamentos [podem ser sobrescritos](http://en.wikipedia.org/wiki/C_signal_handling), ao passo que alguns outros poucos não.

Como exemplos, podemos citar os seguintes sinais:

- **SIGHUP:** Utilizado quando um terminal de controle é fechado;
    - O comportamento _default_ é parar a execução, embora muitos _deamons_ realizem operações de _reload_ ao receber este sinal;
- **SIGTERM:** Informa que o programa deve terminar a execução;
    - Possui o mesmo comportamento _default_ que o SIGHUP;
    - É o sinal padrão enviado pelos comandos `kill` e `killall`;
- **SIGINT:** Informa que o programa recebeu uma interrupção pelo terminal de controle;
    - Muito semelhante ao SIGTERM;
    - Ocorre ao pressionar `CTRL+C` no terminal onde o processo está executando em _foreground_;
- **SIGKILL:** Finaliza forçadamente o programa;
    - É parecido com o SIGINT e o SIGTERM, mas não pode ser sobrescrito;
- **SIGTSTP:** Informa que o programa deve ser pausado (colocado em estado _suspended_);
    - Ocorre ao pressionar `CTRL+Z` no terminal em um processo em _foreground_;
- **SIGSTOP:** Pausa forçadamente um processo;
    - É semelhante ao SIGTSTP, porém, ao [contrário do primeiro](http://stackoverflow.com/a/11888074), não pode ser sobrescrito;
- **SIGCONT:** Retorna um processo pausado (_suspended_) para a fila de prontos (estado _running_);
- **SIGCHLD:** Informa a um processo pai que algum filho terminou a execução, foi suspendido (_suspended_) ou resumido (voltando ao estado _running_).

O comando [`kill`](http://en.wikipedia.org/wiki/Kill_(command)) pode ser utilizado para enviar sinais a um processo;

Sobrescrevendo sinais
---------------------

Vamos agora apresentar um programa que irá sobrescrever o comportamento padrão de um sinal (_signal handler_). Iremos chamá-lo de **i_will_survive.c**:

    #!c
    #include <signal.h>
    #include <stdio.h>
    #include <stdlib.h>
    
    // handler for common signals that terminate process
    static void end_handler(int signal) {
        printf("I will survive, baby!\n");
    }
    
    int main(int argc, char *argv[]) {
        // set handlers
        if ((signal(SIGINT, end_handler) == SIG_ERR) || (signal(SIGHUP, end_handler) ==  
                SIG_ERR) || (signal(SIGTERM, end_handler) == SIG_ERR)) {
            printf("Error while setting a signal handler\n");
            exit(EXIT_FAILURE);
        }   
        while (1) { } // infinite loop
        return 0;  
    }

Este programa define a [função estática](http://codingfreak.blogspot.com/2010/06/static-functions-in-c.html) `end_handler` como o handler dos sinais SIGINT, SIGHUP e SIGTERM. Para isso, é utilizada a função [signal](http://www.cplusplus.com/reference/csignal/signal/). Logo após, ele entra em um loop infinito. 

Se ocorrer algum erro ao definir o _handler_, este programa imprime a mensagem de erro apropriada e sai.

Vamos executá-lo em _foreground_ e, logo após, pressionar algumas vezes `CTRL+C` para enviar sinais SIGINT:

    :::bash
    gcc -o i_will_survive i_will_survive.c
    ./i_will_survive
    > ^CI will survive, baby!
    > ^CI will survive, baby!

Ao receber o sinal, a função `end_handler` é executada e é impresso "I will survive" na tela.

Vamos agora abrir um outro terminal e, após obter o PID do processo, enviar vários sinais usando o comando `kill`:

    :::bash
    ps aux | grep i_will_survive | grep -v grep
    > rarylson       55300  98.5  0.0  2432744    480 s003  R+   11:39PM   0:10.66 ./i_will_survive
    kill 55300
    kill -s SIGHUP 55300
    kill -s SIGINT 55300

Perceba que o primeiro comando `kill` enviará um SIGTERM (o sinal padrão deste comando). 

No primeiro terminal, vemos que o processo continua executando. Pior ainda, após receber cada um dos sinais, ele imprimiu uma mensagem nada humilde na tela:

    :::bash
    > I will survive, baby!
    > I will survive, baby!
    > I will survive, baby!

Agora, no segundo terminal, iremos enviar um sinal SIGKILL:

    :::bash
    kill -s SIGKILL 55300

Desta vez, no primeiro terminal, verificamos que o processo finalmente morreu (**i_will_survive**, sua hora chegou!):

    :::bash
    > Killed: 9

**Obs:** SIGKILL é o sinal de número 9. Assim, `kill -9 55300` (`kill -9` é uma expressão comum nos fóruns sobre Linux) faria exatamente a mesma coisa que o último comando executado.

### Sinais que não podem ser sobrescritos

O [POSIX define](http://en.wikipedia.org/wiki/Unix_signal#POSIX_signals) dois sinais como sinais que não podem ser sobrescritos. Eles já foram apresentados anteriormente: são os sinais SIGSTOP e SIGKILL.

Vamos supor que um certo programador quer sobrescrever o _handler_ de SIGKILL. O que irá ocorrer?

Para realizar este teste, iremos modificar a **linha 13** do programa **i_will_survive.c** para:

    :::c
    // SIG_ERR) || (signal(SIGTERM, end_handler) == SIG_ERR)) {
    SIG_ERR) || (signal(SIGTERM, end_handler) == SIG_ERR) ||
    (signal(SIGKILL, end_handler) == SIG_ERR)) {
    
Recompilando e executando o programa:

    :::bash
    gcc -o i_will_survive i_will_survive.c
    ./i_will_survive
    > Error while setting a signal handler

Ou seja, de fato, não é possível sobrescrever o _handler_ default de SIGKILL (e nem de SIGSTOP).

Implementando stop e reload usando sinais
-----------------------------------------

Agora, iremos implementar um programa em C que atende aos seguintes requisitos:

- Este programa deverá imprimir, de segundo em segundo, um contador e uma string;
- Após cada impressão, este programa deverá incrementar o contador;
- A string será definida em arquivo de configuração.

Para isso, vamos utilizar a biblioteca [**libconfig**](http://www.hyperrealm.com/libconfig/libconfig.html), que permite ler valores de arquivos de configuração.

No Ubuntu, esta biblioteca pode ser instalada através do comando:

    :::bash
    apt-get install libconfig-dev

Logo após, iremos definir nosso arquivo de configuração (**gracefull_stop_reload.cfg**):

    #!cfg
    # string to append in the 'gracefull_stop_reload' output
    add_string = "execution(s)";

Agora, vamos criar o arquivo **gracefull_stop_reload.c**:

    #!c
    #include <stdio.h>
    #include <unistd.h>
    #include <stdlib.h>
    #include <libconfig.h>

    #define CONFIG_FILE "gracefull_stop_reload.cfg"

    int main(int argc, char *argv[]) {
        FILE *f = NULL;
        config_t config = NULL;
        char *add_string = NULL;
        int counter = 0;

        // init and read config
        config_init(&config);
        if(config_read_file(&config, CONFIG_FILE) == CONFIG_FALSE) {
            printf("Error while reading config file\n");
            config_destroy(&config);
            exit(EXIT_FAILURE);
        }
        // read 'add_string'
        config_lookup_string(&config, "add_string", (const char**)(&add_string));
        // print 'counter + add_string' every second 
        counter = 1;
        while (1) {
            printf("%d %s\n", counter, add_string);
            counter++;
            sleep(1);
        }
        //cleanup
        config_destroy(&config);  
        return 0;
    }

Este programa inicia a _struct_ `config` com as informações do arquivo de configuração. Em seguida, ele carrega, como uma string, a configuração `add_string` na variável de mesmo nome. Por último, ele entra em loop infinito e, em cada interação, imprime o contador, a string, e dorme por um segundo.

Agora, vamos compilar e executar este programa. Devemos passar a diretiva `-lconfig` para [_linkar_ o nosso programa com a biblioteca **libconfig**](http://www.hyperrealm.com/libconfig/libconfig_manual.html#Using-the-Library-from-a-C-Program).

    :::bash
    gcc -o gracefull_stop_reload gracefull_stop_reload.c -lconfig
    ./gracefull_stop_reload
    > 1 execution(s)
    > 2 execution(s)
    > [...]

O programa funciona bem. Entretanto, possui as seguintes características:

- Ao receber um sinal para terminar a execução, nosso script perderá o contador do número de execuções (voltará a contar de 1);
- Ao alterarmos o arquivo de configuração, para que esta mudança se reflita no programa, temos que finalizá-lo e iniciá-lo novamente.

Estes são problemas semelhantes aos enfrentados na implementação de _deamons_: geralmente, deseja-se que eles possuam um comando para parar de forma segura, mantendo a consistênca dos dados (_gracefull stop_), e um comando para recarregar as configurações.

Assim, vamos alterar o código do nosso programa para que:

- Seja possível guardar o estado do contador entre execuções sucessivas (se o programa for parado adequadamente);
- Seja possível recarregar as configurações a qualquer momento.

Desde modo, o código de **gracefull_stop_reload.c** ficará:

    #!c
    #include <stdio.h>
    #include <unistd.h>
    #include <stdlib.h>
    #include <signal.h>
    #include <libconfig.h>
    
    #define CONFIG_FILE "gracefull_stop_reload.cfg"
    #define STATE_FILE "gracefull_stop_reload.state"

    // global vars
    static config_t config;
    static char *add_string;
    static int counter;

    // get the last value of counter
    int init_counter() {
        FILE *f;
        int counter;

        if(!(f = fopen(STATE_FILE, "r"))) { // if there isn't file, return 1 
            counter = 1;
        } else { // else, return last count
            fscanf(f, "%d", &counter);
        }
        return counter;
    }

    // persist counter in the STATE_FILE
    void persist_counter(int counter) {
        FILE *f;

        if(!(f = fopen(STATE_FILE, "w"))) {
            // error
            printf("Error while openning state file\n");
            exit(EXIT_FAILURE);
        }
        // insert 'counter' and close file
        fprintf(f, "%d", counter);
        fclose(f);
    }

    // read configuration and get 'add_string'
    void read_config(config_t *config, const char **add_string) {
        // read config
        if(config_read_file(config, CONFIG_FILE) == CONFIG_FALSE) {
            printf("Error while reading config file\n");
            config_destroy(config);
            exit(EXIT_FAILURE);
        }
        // read 'add_string'
        config_lookup_string(config, "add_string", add_string);
    }

    // handler. shut down gracefully
    static void stop_handler(int signal) {
        // persist counter
        persist_counter(counter);
        // now, we can shutdown safelly
        exit(EXIT_SUCCESS);
    }

    // handler. reload config file
    static void reload_handler(int signal) {
        read_config(&config, (const char **)(&add_string));
    }

    int main(int argc, char *argv[]) {
        // set handlers
        // SIGINT and SIGTERM: gracefull stop
        if ((signal(SIGINT, stop_handler) == SIG_ERR) ||
                (signal(SIGTERM, stop_handler) == SIG_ERR)) {
            printf("Error while setting a signal handler\n");
            exit(EXIT_FAILURE);
        }
        // SIGHUP: reload
        if (signal(SIGHUP, reload_handler) == SIG_ERR) {
            printf("Error while setting a signal handler\n");
            exit(EXIT_FAILURE);
        }
        // init and read config
        config_init(&config);
        read_config(&config, (const char **)(&add_string));
        // print 'counter + add_string' every second 
        counter = init_counter(); // get last counter
        while (1) {
            printf("%d %s\n", counter, add_string);
            counter++;
            sleep(1);
        }
        // cleanup
        config_destroy(&config);
        return 0;
    }


Agora, ao receber o sinal SIGINT ou SIGTERM, o programa irá persistir o valor do contador, recarregando-o na próxima execução. Para testarmos esta funcionalidade, devemos recompilar o processo e iniciá-lo novamente e, na sequência, enviar um sinal SIGTERM a partir de outro terminal:

    :::bash
    ps aux | grep gracefull_stop_reload | grep -v grep
    > root      3806  0.0  0.0   6380   560 pts/0    S+   17:06   0:00 ./gracefull_stop_reload
    kill -s SIGTERM 3806

Vontando ao primeiro terminal e executando novamente o processo, vemos que o contador foi corretamente persistido:

    :::bash
    ./gracefull_stop_reload
    > 1 execution(s)
    > [...]
    > 40 execution(s)
    # script stopped here
    ./gracefull_stop_reload 
    > 41 execution(s)
    > [...]
    
Além disso, ao alterarmos o valor do arquivo de configuração, poderemos recarregá-lo enviando um sinal SIGHUP para a aplicação. Para isso, iremos editar o arquivo de configuração (**gracefull_stop_reload.cfg**) no segundo terminal:

    #!cfg
    # string to append in the 'gracefull_stop_reload' output
    add_string = "execution(s)... I am so tired ;(";

Agora, iremos enviar o sinal apropriado para que o programa realize o reload:

    :::bash
    kill -s SIGHUP 3806

Por fim, verificamos que o programa passou a utilizar nosso novo arquivo de configuração:

    :::bash
    > 48 execution(s)
    > 49 execution(s)... I am so tired ;(
    > [...]

Esta implementação lembra o que ocorre em vários _deamons_. Por exemplo, o Nginx e o Apache, conforme a [sessão _Signals_ do manual do Nginx](http://www.rootr.net/man/man/nginx/8) e a [página _Stopping and Restart_ do manual do Apache](http://httpd.apache.org/docs/2.2/stopping.html), processam sinais para realizarem operações de stop e reload.


Referências
-----------

- [Wikipedia - Unix signal](http://en.wikipedia.org/wiki/Unix_signal)
- [Linux Man - Signal](http://man7.org/linux/man-pages/man7/signal.7.html)
- [The Linux Kernel - Signals](http://www.win.tue.nl/~aeb/linux/lk/lk-5.html)
