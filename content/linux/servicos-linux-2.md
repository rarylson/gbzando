Title: Serviços no Linux: Criando init scripts para uso em produção (parte 2)
Date: 2016-09-08 13:35
Tags: linux, c, daemons, servers, shell-script
Slug: servicos-linux-2
Category: Linux
Summary: Neste artigo, mostramos como construir um SysV Init script (scripts do diretório /etc/init.d) profissional, que considera os problemas mais comuns, pronto para uso em produção. Além disso, apresentamos a especificação LSB Init.

No primeiro artigo desta série, [Serviços no Linux: Criando e controlando serviços via init.d (parte 1)]({filename}servicos-linux.md), mostramos de forma geral como podemos controlar os _daemon_ e registrá-los na hora do boot. Mostramos também alguns exemplos de _SysV Init scripts_, scripts que ficam em `/etc/init.d` e que são geralmente usados através do comando `service`. Apresentamos vários conceitos importantes sobre estes scripts e mostrando problemas que eles possuíam.

Neste post, vamos evoluir os nossos SysV init scripts, tornando-os scripts maduros e profissionais, bons para uso em produção.

Vamos apresentar, inicialmente, a parte da especificação _LSB_ que padroniza a criação destes scripts, e depois vamos mostrar como usá-la para criar scripts realmente profissionais.

Ao apresentar exemplos, iremos contruí-los a partir dos exemplos apresentados no artigo anterior. Vamos pressupor que o nosso servidor de testes está exatamente no ponto em que o deixamos no final do artigo anterior (com o nosso daemon de teste, o `gb_daemon`, compilado, instalado e rodando no sistema, e usando a versão do script `/etc/init.d/gb_daemon` do final do artigo).

Assim, para entender este artigo, vale a pena dar uma olhadinha no artigo anterior [Serviços no Linux: Criando e controlando serviços via init.d (parte 1)]({filename}servicos-linux.md), especialmente se você quiser ir além e seguir os exemplos aqui apresentados.

A especificação LSB Init
------------------------

Dada a importância e ao amplo uso dos SysV Init scripts, surgiu a necessidade da existência de uma especificação que padronizasse o funcionamento deles. A especificação [**LSB Init**](https://wiki.debian.org/LSBInitScripts) foi criada, então, para este fim.

Ela define, dentre outras coisas:

- Que ações (como `start` e `stop`) devem existir em um script;
- Que _exit status_ devem ser retornados pelas ações de um script em cada caso;
- Como as mensagens de _output_ (por exemplo, uma mensagem informando que o daemon foi inicializado com sucesso) devem ser padronizadas;
- Como as dependências de um script (que serviços devem estar rodando antes dele ser iniciado) devem ser informadas.

Vamos entrar um pouquinho mais em detalhes e mostrar alguns exemplos...

Primeiramente, essas são as principais ações definidas nessa especificação:

- As ações `start`, `stop`, `restart`, `status` e `force-reload` são obrigatórias;
    - Os significados de cada uma dessas ações já foram explicados [no artigo anterior, no comecinho da sessão "Criando e controlando serviços no SysV Init"](/servicos-linux/#criando-e-controlando-servicos-no-sysv-init). Cabe ressaltar que esses significados, embora mostrados anteriormente, são também padronizados pela especificação LSB Init;
- A ação `reload`, por sua vez, é opcional.

Em relação aos códigos de erro, a LSB Init diz o seguinte:

- A ação `status` deve retornar _exit codes_ apropriados para cada situação, cada qual com um significado padronizado. Os principais são:
    - 0, se o processo está rodando normalmente;
    - 1, se o programa não está rodando, mas o seu pidfile existe;
    - 3, se o programa não está rodando e ele foi finalizado corretamente (nenhum pidfile no sistema);
- Já os demais comandos (como o `start` e o `stop`) devem retornar 0 em caso de sucesso e 1 em caso de erros;
    - Códigos de erro maiores que 1 também podem ser usados para indicar erros mais específicos. Esses códigos também são definidos na especificação;
    - Alguns casos de excessão, como rodar `start` quando o serviço já está rodando, ou rodar `stop` quando o serviço já está parado, devem ser considerados como sucesso e retornar zero;
    - Isso não muda o fato, entretanto, de que não devemos iniciar um daemon caso uma instância sua já esteja rodando, ou de que não devemos enviar um sinal `SIGTERM` para um processo qualquer se o daemon já parou de rodar. Continuamos que ter que tratar adequadamente essas excessões e, se julgarmos necessário, informar o administrador do sistema da excessão. O detalhe aqui é que, após tratarmos adequadamente uma excessão, temos que retornar sucesso.

Uma boa referência sobre as ações da LSB e os exit codes está em [linuxbase.org - LBS 3.0 - Init Script Actions](https://refspecs.linuxbase.org/LSB_3.0.0/LSB-PDA/LSB-PDA/iniscrptact.html). Outras políticas interessantes sobre a criação desses scripts podem ser encontradas em [Debian Policy Manual - System run levels and init.d scripts - Writing the scripts](https://www.debian.org/doc/debian-policy/ch-opersys.html#s-writing-init).

A LBS também define algumas funções em shell script que devem ser disponibilizados como uma biblioteca, podendo assim ser reutilizadas pelos SysV Init scripts para implementar, de uma forma mais fácil, as ações da especificação LSB. Por exemplo, podemos citar a função `status_of_proc`, que pode ser usada para retornar o _LSB status_ apropriado (exit code que a ação `status` deveria retornar) de um processo. No caso do Ubuntu, essa e outra funções são implementadas na biblioteca `/lib/lsb/init-functions`.

Para demonstrar o funcionamento do que foi apresentado acima, vamos fazer um pequeno teste para retornar o status do nosso daemon, que está rodando no momento em nossa máquina de testes:

```console
$ . /lib/lsb/init-functions
$ status_of_proc -p /run/gb_daemon.pid gb_daemon "GB daemon gb_daemon"
 * GB daemon gb_daemon is running
$ echo $?
0
$ service gb_daemon stop
GB daemon stopped
$ status_of_proc -p /run/gb_daemon.pid gb_daemon "GB daemon gb_daemon"
 * GB daemon gb_daemon is not running
$ echo $?
3
```

Em relação ao output de uma ação, a LSB até dá várias recomendações e sugestões, mas não define nada muito formal. Entretanto, ela define algumas funções em shell script que devem ser usadas pelos scripts para imprimir saídas padronizados, como a `log_success_msg` e a `log_failure_msg`.

Vamos verificar como estes comandos funcionam:

```console
$ log_success_msg "GB daemon started"
 * GB daemon started
$ log_failure_msg "GB daemon not started"
 * GB daemon not started
```

**Obs:** Embora a saída anterior seja apresentada em uma única cor ao leitor, a função `log_failure_msg`, no terminal do Ubuntu, imprime o caracter "*" na cor vermelha. Isso facilita ao administrador a visualmente identificar que algo deu errado. Teste você mesmo!

Além das funções de saída definidas pela LSB, os sistemas operacionais costumam definir funções adicionais para facilitar ainda mais o trabalho de geração de saídas padronizadas. As funções `log_daemon_msg` e `log_end_msg`, por exemplo, podem ser usadas para gerar as saídas (e retornar os respectivos exit codes) para as ações `start` e `stop` de um init script.

Vamos mostrar alguns exemplos:

```console
$ log_daemon_msg "Starting GB Daemon" "gb_daemon" && log_end_msg 0
 * Starting GB Daemon gb_daemon                                         [ OK ]
$ echo $?
0
$ log_daemon_msg "Starting GB Daemon" "gb_daemon" && log_end_msg 1
 * Starting GB Daemon gb_daemon                                         [fail]
$ echo $?
1
```

Mais informações sobre as funções definidas pela LSB são encontradas em [linuxbase.org - LBS 3.0 - Init Script Functions](https://refspecs.linuxbase.org/LSB_3.0.0/LSB-PDA/LSB-PDA/iniscrptfunc.html).

**Obs:** Assim como ocorreu com outras funções de saídas, embora todas as saídas do exemplo acima sejam apresentadas em uma única cor ao leitor, o comando `log_end_msg 1`, no terminal do Ubuntu, imprime a palavra "_fail_" na cor vermelha. Fique à vontade para testar.

Por fim, a LSB define convensões de comentários (_Comment Convensions_), que são comentários que devem ser inseridos em um init script para que o sistema operacional saiba registrar apropriadamente o serviço no boot do sistema. Vamos chamá-los de _init info comments_, ou simplesmente de _init info_. Esses comentários devem ficar contidos entre duas linhas de comentários especiais, mostradas a seguir:

```sh
### BEGIN INIT INFO
### END INIT INFO
```

A seguir, vamos mostrar alguns comentários init info que podem ser usados pelo nosso `gb_daemon`:

```sh
### BEGIN INIT INFO
# Provides:          gb_daemon
# Required-Start:    $local_fs $syslog
# Required-Stop:     $local_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: GBzando daemon
# Description:       The GBzando daemon.
#                    A test daemon which daemonizes itself, uses a pidfile and
#                    writes messages to the syslog.
### END INIT INFO
```

Vamos explicar o que eles significam:

- O nome do serviço (na verdade, o nome técnico usado pela LSB é _facility_) que o init script inicializa deve ser informado em `Provides`;
    - No nosso exemplo, após iniciar o nosso serviço, informamos que a facility `gb_daemon` estará funcionando após o serviço estar rodando;
- Em `Required-Start`, colocamos os nomes das facilities que precisam estar funcionando para que possamos iniciar esse serviço com sucesso (ação `start`);
    - Em outras palavras, listamos aqui as dependências do nosso serviço;
    - A ideia é que, durante o boot, o sistema operacional aguarde até que todas as facilities especificadas estejam funcionando corretamente para, somente depois, iniciar o nosso serviço;
    - Podemos aguardar por facilities definidas em outros scripts. Por exemplo, se um outro init script especificar "`# Required-Start: gb_daemon`", ele irá esperar até que nosso serviço `gb_daemon` seja rodando para, somente depois, ser iniciado (considerando que o nosso daemon especificou "`# Provides: gb_daemon`" em seu init info);
    - Além das facilities definidas em outros init scripts, existem facilities especiais, definidas pelo sistema operacional (elas começam com o caracter `$`). No nosso exemplo acima, o serviço `gb_daemon` irá esperar pelas facilities `$local_fs` e `$syslog`, esperando até que todos sistemas de arquivos locais estejam montados, e até que o sistema _syslog_ esteja rodando. Somente depois, o sistema operacional irá iniciar o nosso serviço;
- A linha `Required-Stop` possui funcionamento análogo à `Required-Start`, com o nome das facilities que devem estar funcionando na hora de desativar o serviço (ação `stop`);
- Em `Default-Start`, informamos em quais runlevels o nosso daemon deve estar rodando;
    - Como consequência, ao realizar o boot usando um destes runlevels, o nosso daemon será iniciado automaticamente durante a inicialização do sistema;
- Já na linha `Default-Stop`, informamos em quais runlevels ele não deve estar rodando por padrão;
- Em `Short-Description`, colocamos uma breve descrição, de uma linha, do nosso serviço;
- Uma descrição mais completa pode ser informada em `Description`.

Lembra-se que, no artigo anterior, na sessão [Registrando serviços do SysV Init no boot do sistema](/servicos-linux/#registrando-servicos-do-sysv-init-no-boot-do-sistema), alguns _warnings_ surgiram quando rodamos o comando `update-rc.d`? E lembra-se que falamos que, no futuro, iríamos resolver isso? Pois é... Chegou a hora de falarmos sobre eles!

Conforme explicamos no artigo passado, o comando `update-rc.d` é responsável por criar os links simbólicos adequados para que o serviço inicie corretamente na hora do boot. Em cada runlevel, ele tem que criar o link simbólico começando com `S` (serviço deve estar iniciado no runlevel) ou `K` (serviço deve estar parado no runlevel). Além disso, os links simbólicos possuem um número logo após a primeira letra, usado para ordenar os serviços (quais devem subir antes e quais devem subir depois).

Agora vamos as novidades... O programa `update-rc.d` utiliza as informações do init info para saber como os links simbólicos devem ser criados. Por exemplo, no caso, uma vez que usamos "`Default-Start: 2 3 4 5`" e "`Required-Start: $local_fs $syslog`", o `update-rc.d` vai criar o nosso link simbólico começando com `S` no runlevels de 2 a 5, além de usar um número suficientemente alto para garantir que nosso scripts só suba no sistema depois da montagem dos sistemas de arquivos locais e do syslog. Sem o init info, tudo que ele pode fazer é usar valores padrão (que muitas vezes funcionam, mas às vezes não). É exatamente por isso que os warnings são exibidos.

Ou seja, esses comentários são importantes para que os nossos daemons sejam iniciados corretamente na hora do boot. Sem eles, poderíamos subir um daemon no momento errado, fazendo com que muitas coisas podessem não funcionar.

A especificação detalhada sobre os comentários init info pode ser vista em [linuxbase.org - LBS 3.0 - Comment Conventions for Init Scripts](https://refspecs.linuxbase.org/LSB_3.0.0/LSB-PDA/LSB-PDA/initscrcomconv.html). A lista com os facilities especiais, definidos pelo sistema, pode ser encontrada em [linuxbase.org - LBS 3.0 - Facility Names](https://refspecs.linuxbase.org/LSB_3.0.0/LSB-PDA/LSB-PDA/facilname.html).

Perceba que usar a LSB nos garante um maior poder aos nossos scripts. Por exemplo, um administrador de sistemas saberá que ele sempre poderá contar com uma ação como a `status` nos init scripts disponíveis, já que ela é obrigatória pela LSB. Além disso, como os exit codes e as saídas na tela são padronizadas, fica bem mais fácil criar programa e scripts que reutilizem init scripts existem no sistema em sua lógica.

### O comando start-stop-daemon

Além da biblioteca mostrada na sessão anterior, o Ubuntu também fornece o comando `start-stop-daemon`. Embora este comando não faça parte da LSB, ele ajuda a implementar as tarefas rotineiras de iniciar e parar um daemon, exatamente como definido pela especificação LSB. Ele trata vários dos casos de excessão mostrados anteriormente, como conferir se o pidfile existe antes de tentar iniciar um daemon, conferir se um daemon está de fato rodando antes de tentar pará-lo, além de tratar o problema do _stale pidfile_.

Para demonstrar o funcionamento desse comando, vamos usá-lo para iniciar novamente o nosso daemon:

```console
$ start-stop-daemon --start --pidfile /run/gb_daemon.pid \
>   --exec /usr/local/bin/gb_daemon
$ status_of_proc -p /run/gb_daemon.pid gb_daemon "GB daemon gb_daemon"
 * GB daemon gb_daemon is running
```

Esse comando (usado com o parâmetro `--start`) verifica se o pidfile existe e, em caso positivo, também verifica se o daemon está rodando apropriadamente (isto é, não temos um stale pidfile). Caso o daemon não esteja rodando, ele inicia o daemon e, depois, espera de forma assíncrona até que o seu pidfile tenha sido criado com sucesso, substituindo assim, de forma bastante eficiente, a função do nosso comando `sleep 1`, usado no SysV Init script da sessão anterior.

O `start-stop-daemon` também pode ser usado para finalizaz o daemon:

```console
$ start-stop-daemon --stop --pidfile /run/gb_daemon.pid \
>   --exec /usr/local/bin/gb_daemon --retry TERM/30/KILL/5
$ status_of_proc -p /run/gb_daemon.pid gb_daemon "GB daemon gb_daemon"
 * GB daemon gb_daemon is not running
```

No exemplo acima (usado com o parâmetro `--stop`), o `start-stop-daemon` envia um sinal `SIGTERM` para o daemon em questão e aguarda de forma assincrona até este ser finalizado. Ao finalizar, a função ainda verifica se o daemon deixou algum pidfile sobrando, apagando-o caso necessário.

A novidade aqui é a opção `--retry` com o valor `TERM/30/KILL/5`. No nosso exemplo, após enviar o sinal `SIGTERM`, esperamos no máximo 30 segundos até que o daemon finalize. Caso contrário, entendemos que algo deu errado (por exemplo, o programa travou) e enviamos um sinal `SIGKILL`, forçando sua finalização abrupta (esperando até 5 segundos para confirmar que a finalização abrupta ocorreu). Caso apenas usássemos `TERM/30`, iríamos apenas enviar o sinal `SIGTERM` e retornar erro caso o programa não finalizasse no tempo especificado.

Por fim, convém saber que o comando `start-stop-daemon` retorna diferentes exit codes para cada caso de excessão. Como exemplo, caso ele retorne 1, é porque o daemon já estava rodando antes de um `start`, ou porque ele já havia parado antes de um `stop`.

Criando um SysV Init script para uso em produção
------------------------------------------------

Nesta sessão, vamos melhorar mais ainda o nosso SysV Init script sobre três aspectos diferentes:

- Vamos tornar os nossos scripts melhor padronizados, respeitando a especificação LSB;
- Vamos corrigir os problemas que o nosso último script ([criado no artigo anterior](/servicos-linux/#criando-um-sysv-init-script-melhor)) possui;
- Vamos usar funções e comandos que já existem no Ubuntu e em sistemas semelhantes para facilitar nossa implementação.

Com isso, teremos um SysV Init script simples, fácil de criar e entender e, ao mesmo tempo, sem nenhum dos problemas apresentados anteriormente. Será um script ótimo para uso em produção.

Para isso, antes, vamos parar o nosso serviço e remover o nosso script anterior:

```console
$ rm /etc/init.d/gb_daemon
$ update-rc.d gb_daemon remove
```

E, depois, vamos criar o nosso novo init script em `/etc/init.d/gb_daemon`:

```
#!sh
#!/bin/sh
### BEGIN INIT INFO
# Provides:          gb_daemon
# Required-Start:    $local_fs $syslog
# Required-Stop:     $local_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: GBzando daemon
# Description:       The GBzando daemon.
#                    A test daemon which daemonizes itself, uses a pidfile and
#                    writes messages to the syslog.
### END INIT INFO

NAME="gb_daemon"
DESC="GB daemon"
PIDFILE="/run/$NAME.pid"
DAEMON="/usr/local/bin/$NAME"

[ -x "$DAEMON" ] || exit 0

. /lib/lsb/init-functions

do_start () {
    start-stop-daemon --start --quiet --pidfile "$PIDFILE" --exec "$DAEMON"
}

do_stop() {
    start-stop-daemon --stop --quiet --pidfile "$PIDFILE" --exec "$DAEMON" \
        --retry TERM/30/KILL/5
}

case "$1" in
    start)
        log_daemon_msg "Starting $DESC" "$NAME"
        do_start
        retval="$?"
        case "$retval" in
            0|1)
            	[ "$retval" -eq 1 ] && log_progress_msg "already started"
                log_end_msg 0
                ;;
            *)
                log_end_msg 1
                exit 1
                ;;
        esac
        ;;
    stop)
        log_daemon_msg "Stopping $DESC" "$NAME"
        do_stop
        retval="$?"
        case "$retval" in
            0|1)
            	[ "$retval" -eq 1 ] && log_progress_msg "already stopped"
                log_end_msg 0
                ;;
            *)
                log_end_msg 1
                exit 1
                ;;
        esac
        ;;
    restart|force-reload)
        "$0" stop
        "$0" start
        ;;
    status)
        status_of_proc -p "$PIDFILE" "$DAEMON" "$DESC $NAME"
        exit "$?"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|force-reload|status}"
        exit 2
        ;;
esac
```

Depois de entender os scripts do artigo anterior, e de ver a sessão anterior deste artigo (sobre a LSB Init e o `start-stop-daemon`), fica bem mais fácil entender o script acima. Ele funciona da seguinte maneira:

- Declaramos, logo no início do script, os comentários init info do nosso serviço;
- Mudamos um pouco o nome das nossas variáveis;
    - Estamos usando este nomes (`NAME`, `DESC`, `PIDFILE` e `DAEMON`) porque eles são comuns na implementação de SysV Init scripts. Usando nomes consagrados pelo uso, facilitamos o entendimento do nosso script por administradores de sistema que conheçam outros init scripts;
- Uma outra novidade é que carregamos a bibliota que contém as função da LSB Init (comando `. /lib/lsb/init-functions`);
- Implementamos as nossas funções `do_start` e `do_stop` usando o comando `start-stop-daemon`;
    - Conforme já mostrado anteriomente, isso faz com que vários casos de excessão sejam tratados, incluindo os problemas do _stale pidfile_ e da espera pela criação/remoção de pidfiles de forma eficiente;
- Para implementar as ações `start` e `stop`, usamos as funções `log_daemon_msg` e `log_end_msg` para imprimir as saídas na tela de forma padronizada;
    - Uma novidade: caso ocorra uma exceção, como receber a ação `start` quando o daemon já está rodando (lembre-se que, nestes casos, `start-stop-daemon` retorna 1), usamos a função `log_progress_msg` para informar a ocorrência da excessão ao administrador;
    - No Debian, a função `log_progress_msg` imprime uma observação na tela. Já no Ubuntu, por uma decisão da comunidade (pessoal que contribui com a distribuição), essa função não imprime nada na tela e nem faz nada. De qualquer forma, nós estamos usando essa função no nosso script para deixá-lo conforme um número maior de distribuições;
- A ação `restart` é implementada chamando o nosso próprio script (cujo caminho fica na variável `$0`) duas vezes, uma usando o parâmetro `stop` e a outra usando `start`;
    - Essa é uma forma bem diferente de reaproveitar código se compararmos com o script do artigo anterior, que reutilizava as funções `do_stop` e `do_start` para este fim;
- Usamos a função `status_of_proc` para implementar a ação `status`, imprimindo uma mensagem adequada e retornando o exit code apropriado.

**Obs:** Para facilitar a criação de um Sysv Init script, o Ubuntu disponibiliza um script de exemplo em `/etc/init.d/skeleton`. Podemos usá-lo como base quando precisarmos criar um script. Aliás, se compararmos ele com o script que criamos nessa sessão, veremos que eles são até bem parecidos.

Iremos agora conferir permissão de execução ao nosso script, além de o registrarmos para inicializar no boot do sistema:

```console
$ chmod +x /etc/init.d/gb_daemon
$ update-rc.d gb_daemon defaults
```

Perceba que, desta vez, o comando `update-rc.d` não imprimiu nenhum warning!

E, por fim, vamos testá-lo:

```console
$ service gb_daemon start
 * Starting GB daemon gb_daemon                                          [ OK ]
$ service gb_daemon status
 * GB daemon gb_daemon is running
$ echo $?
0
$ service gb_daemon restart
 * Stopping GB daemon gb_daemon                                          [ OK ]
 * Starting GB daemon gb_daemon                                          [ OK ]
$ service gb_daemon stop
 * Stopping GB daemon gb_daemon                                          [ OK ]
$ service gb_daemon status
 * GB daemon gb_daemon is not running
$ echo $?
3
```

### Um jeito diferente de implementar a ação restart

Nós implementamos a nossa ação de `restart` como a execução, na sequência, das ações de `stop` e de `start`. Essa é uma boa maneira, bastante prática e intuitiva, de implementar essa ação.

Entretanto, algumas pessoas preferem implementar essa ação de uma outra forma. Vamos, através de um exemplo, mostrar esse outro jeito de pensar.

Para isso, vamos modificar o nosso init script (`/etc/init.d/gb_daemon`) e realizar a seguinte mudança:

```diff
         esac
         ;;
     restart|force-reload)
-        "$0" stop
-        "$0" start
+        log_daemon_msg "Restarting $DESC" "$NAME"
+        do_stop
+        retval="$?"
+        case "$retval" in
+            0|1)
+                [ "$retval" -eq 1 ] && \
+                    log_progress_msg "old process already stopped"
+                do_start
+                retval="$?"
+                case "$retval" in
+                    0)
+                        log_end_msg 0
+                        ;;
+                    *)
+                        [ "$retval" -eq 1 ] && \
+                            log_progress_msg "old process still running"
+                        log_end_msg 1
+                        exit 1
+                        ;;
+            *)
+                log_end_msg 1
+                exit 1
+                ;;
+            esac
+        esac
         ;;
     status)
         status_of_proc -p "$PIDFILE" "$DAEMON" "$DESC $NAME"

```

Na nossa nova implementação, nós reutilizamos as funções `do_stop` e `do_start` para realizar um restart. Além disso, tratamos manualmente cada um dos casos de excessão das funções `do_stop` e `do_start`.

O lado ruim com essa implementação é que temos que usar mais código. Entretanto, nós temos muito mais controle sobre sua saída e sobre como cada um dos casos de excessão serão tratados.Muitos scripts usam o primeiro modelo por conta da simplicidade dele, mas vários outros usam um estilo parecido com essa nossa nova versão. Inclusive, o init script de exemplo do Ubuntu (`/etc/init.d/skeleton`) se parece muito mais com a nossa última implementação.

Vamos rodar um `restart` para ver, na prática, o que mudou:

```console
$ service gb_daemon restart
 * Restarting GB daemon gb_daemon                                        [ OK ]
```

Referências
-----------

- [Debian Wiki - LSBInitScripts](https://wiki.debian.org/LSBInitScripts)
- [Debian Policy Manual - System run levels and init.d scripts - Writing the scripts](https://www.debian.org/doc/debian-policy/ch-opersys.html#s-writing-init)
- [linuxbase.org - LBS 3.0 - Init Script Actions](https://refspecs.linuxbase.org/LSB_3.0.0/LSB-PDA/LSB-PDA/iniscrptact.html)
- [linuxbase.org - LBS 3.0 - Init Script Functions](https://refspecs.linuxbase.org/LSB_3.0.0/LSB-PDA/LSB-PDA/iniscrptfunc.html)
- [linuxbase.org - LBS 3.0 - Comment Conventions for Init Scripts](https://refspecs.linuxbase.org/LSB_3.0.0/LSB-PDA/LSB-PDA/initscrcomconv.html)
- [linuxbase.org - LBS 3.0 - Facility Names](https://refspecs.linuxbase.org/LSB_3.0.0/LSB-PDA/LSB-PDA/facilname.html)
