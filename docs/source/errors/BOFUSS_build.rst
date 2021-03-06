
=====================
BOFUSSのビルド時エラー
=====================

`gitのwiki <https://github.com/CPqD/ofsoftswitch13/wiki/OpenFlow-1.3-Tutorial>`_ の"The shortest path..."を参考にビルドするが，``ofdissector`` のソースの一部で ``config.h`` のファイルが見つからないエラー
===================================================

.. code-block::

      default: scons: Reading SConscript files ...
      default: scons: done reading SConscript files.
      default: scons: Building targets ...
      default: g++ -o openflow-common.os -c -fPIC -I. -I/usr/include/wireshark -I/usr/include/glib-2.0 -I/usr/lib/x86_64-linux-gnu/glib-2.0/include openflow-common.cpp
      default: In file included from openflow-common.cpp:5:0:
      default: ./openflow-common.hpp:10:10: fatal error: config.h: No such file or directory
      default:  #include <config.h>
      default:           ^~~~~~~~~~
      default: compilation terminated.
      default: scons: building terminated because of errors.
      default: scons: *** [openflow-common.os] Error 1
  The SSH command responded with a non-zero exit status. Vagrant
  assumes that this means the command failed. The output for this command
  should be in the log above. Please read the output to determine what
  went wrong.

* モジュールが足りない？？？

  * ``sudo apt-get install libconfig-dev`` を試す => だめ

* vagrantなので仕様が違う？？？

  * わかんない

* ubuntuのバージョンのせい？？

  * どっちかというとツールのバージョンのせい

* issueにはない

  * ofdissector側にあった

解決
-------
  * ``sudo apt install -y wireshark-dev`` で解決(mininetのインストールでうまく行ってない？？)

    * `参考 <https://github.com/CPqD/ofdissector/issues/13>`_

mininetのインストールでwarning出しまくっている問題
=============================================

.. code-block::

    default: CMake Warning (dev) at nbnetvm/CMakeLists.txt:883 (GET_TARGET_PROPERTY):
    default:   Policy CMP0026 is not set: Disallow use of the LOCATION target property.
    default:   Run "cmake --help-policy CMP0026" for policy details.  Use the cmake_policy
    default:   command to set the policy and suppress this warning.
    default: 
    default:   The LOCATION property should not be read from target "makenetilscanner".
    default:   Use the target name directly with add_custom_command, or use the generator
    default:   expression $<TARGET_FILE>, as appropriate.
    default: 
    default: This warning is for project developers.  Use -Wno-dev to suppress it.
    default: CMake Warning (dev) at nbnetvm/CMakeLists.txt:884 (GET_TARGET_PROPERTY):
    default:   Policy CMP0026 is not set: Disallow use of the LOCATION target property.
    default:   Run "cmake --help-policy CMP0026" for policy details.  Use the cmake_policy
    default:   command to set the policy and suppress this warning.
    default: 
    default:   The LOCATION property should not be read from target "makeopcodetable".
    default:   Use the target name directly with add_custom_command, or use the generator
    default:   expression $<TARGET_FILE>, as appropriate.
    default: 
    default: This warning is for project developers.  Use -Wno-dev to suppress it.
    default: CMake Warning (dev) at nbnetvm/CMakeLists.txt:885 (GET_TARGET_PROPERTY):
    default:   Policy CMP0026 is not set: Disallow use of the LOCATION target property.
    default:   Run "cmake --help-policy CMP0026" for policy details.  Use the cmake_policy
    default:   command to set the policy and suppress this warning.
    default: 
    default:   The LOCATION property should not be read from target "netvmburg".  Use the
    default:   target name directly with add_custom_command, or use the generator
    default:   expression $<TARGET_FILE>, as appropriate.
    default: 
    default: This warning is for project developers.  Use -Wno-dev to suppress it.
    default: -- Configuring done
    default: -- Generating done
    default: -- Build files have been written to: /home/vagrant/module/netbee/src
    default: make: Warning: File 'Makefile' has modification time 0.73 s in the future
    default: make[1]: Warning: File 'CMakeFiles/Makefile2' has modification time 1.7 s in the future
    default: make[2]: Warning: File 'nbsockutils/CMakeFiles/nbsockutils.dir/flags.make' has modification time 1.7 s in the future
    default: Scanning dependencies of target nbsockutils
    default: make[2]: warning:  Clock skew detected.  Your build may be incomplete.
    default: make[2]: Warning: File 'nbsockutils/CMakeFiles/nbsockutils.dir/flags.make' has modification time 1.6 s in the future
    default: [  0%] Building C object nbsockutils/CMakeFiles/nbsockutils.dir/__/nbee/globals/debug.c.o
    default: cc1: warning: command line option ‘-std=c++11’ is valid for C++/ObjC++ but not for C
    default: [  1%] Building C object nbsockutils/CMakeFiles/nbsockutils.dir/__/nbee/globals/utils.c.o
    default: cc1: warning: command line option ‘-std=c++11’ is valid for C++/ObjC++ but not for C
    default: [  1%] Building C object nbsockutils/CMakeFiles/nbsockutils.dir/sockutils.c.o
    default: cc1: warning: command line option ‘-std=c++11’ is valid for C++/ObjC++ but not for C
    default: [  2%] Linking C shared library libnbsockutils.so
    default: make[2]: warning:  Clock skew detected.  Your build may be incomplete.
    default: [  2%] Built target nbsockutils
    default: make[2]: Warning: File 'nbnetvm/tools/netvmburg/CMakeFiles/netvmburg.dir/flags.make' has modification time 0.98 s in the future
    default: [  3%] Generating parser.cpp
    default: Scanning dependencies of target netvmburg
    default: make[2]: warning:  Clock skew detected.  Your build may be incomplete.
    default: make[2]: Warning: File 'nbnetvm/tools/netvmburg/CMakeFiles/netvmburg.dir/flags.make' has modification time 0.81 s in the future
    
    (略)

* mininetのissue確認すべし

wiresharkとの互換性の問題
=======================

.. code-block:: 

  scons: Reading SConscript files ...
  scons: done reading SConscript files.
  scons: Building targets ...
  g++ -o openflow-common.os -c -fPIC -I. -I/usr/include/wireshark -I/usr/include/glib-2.0 -I/usr/lib/x86_64-linux-gnu/glib-2.0/include openflow-common.cpp
  In file included from openflow-common.cpp:9:0:
  ./of13/openflow-130.hpp:12:0: warning: "PROTO_TAG_OPENFLOW_VER" redefined
  #define PROTO_TAG_OPENFLOW_VER "OFP 1.3"
  
  In file included from openflow-common.cpp:8:0:
  ./of12/openflow-120.hpp:13:0: note: this is the location of the previous definition
  #define PROTO_TAG_OPENFLOW_VER "OFP 1.2"
  
  openflow-common.cpp: In function 'void dissect_openflow(tvbuff_t*, packet_info*, proto_tree*)':
  openflow-common.cpp:27:7: error: 'tvb_length' was not declared in this scope
    if (tvb_length(tvb) < OFP_MIN_PACKET_SIZE) // This isn't openflow
        ^~~~~~~~~~
  openflow-common.cpp:27:7: note: suggested alternative: 'ftype_length'
    if (tvb_length(tvb) < OFP_MIN_PACKET_SIZE) // This isn't openflow
        ^~~~~~~~~~
        ftype_length
  openflow-common.cpp: In function 'void proto_reg_handoff_openflow()':
  openflow-common.cpp:58:79: error: invalid conversion from 'void (*)(tvbuff_t*, packet_info*, proto_tree*) {aka void (*)(tvbuff*, _packet_info*, _proto_node*)}' to 'dissector_t {aka int (*)(tvbuff*, _packet_info*, _proto_node*, void*)}' [-fpermissive]
      openflow_handle = create_dissector_handle(dissect_openflow, proto_openflow);
                                                                                ^
  In file included from ./openflow-common.hpp:28:0,
                  from openflow-common.cpp:5:
  /usr/include/wireshark/epan/packet.h:550:34: note:   initializing argument 1 of 'dissector_handle* create_dissector_handle(dissector_t, int)'
  WS_DLL_PUBLIC dissector_handle_t create_dissector_handle(dissector_t dissector,
                                    ^~~~~~~~~~~~~~~~~~~~~~~
  openflow-common.cpp:59:5: error: 'dissector_add' was not declared in this scope
      dissector_add("tcp.port", OFP_TCP_PORT, openflow_handle);
      ^~~~~~~~~~~~~
  openflow-common.cpp:59:5: note: suggested alternative: 'dissector_t'
      dissector_add("tcp.port", OFP_TCP_PORT, openflow_handle);
      ^~~~~~~~~~~~~
      dissector_t
  openflow-common.cpp: In function 'void proto_register_openflow()':
  openflow-common.cpp:78:66: error: invalid conversion from 'void (*)(tvbuff_t*, packet_info*, proto_tree*) {aka void (*)(tvbuff*, _packet_info*, _proto_node*)}' to 'dissector_t {aka int (*)(tvbuff*, _packet_info*, _proto_node*, void*)}' [-fpermissive]
    register_dissector("openflow", dissect_openflow, proto_openflow);
                                                                    ^
  In file included from ./openflow-common.hpp:28:0,
                  from openflow-common.cpp:5:
  /usr/include/wireshark/epan/packet.h:520:34: note:   initializing argument 2 of 'dissector_handle* register_dissector(const char*, dissector_t, int)'
  WS_DLL_PUBLIC dissector_handle_t register_dissector(const char *name, dissector_t dissector, const int proto);
                                    ^~~~~~~~~~~~~~~~~~
  scons: *** [openflow-common.os] Error 1
  scons: building terminated because of errors.

* `これ <https://github.com/legoscia/ofdissector.git>`_ を試してみる( `issue 2 <https://github.com/CPqD/ofdissector/issues/2>`_ )



BOFUSSに依存するライブラリがインストールできない( ``vagrat-2021-04-29-11-38.log`` )
========================================================================================

.. code-block::

  ==> default: Running provisioner: shell...
    default: Running: inline script
    default: WARNING: 
    default: apt
    default:  
    default: does not have a stable CLI interface. 
    default: Use with caution in scripts.
    default: Reading package lists...
    default: Building dependency tree...
    default: Reading state information...
    default: E
    default: : 
    default: Unable to locate package libxerces-c3.1
    default: E
    default: : 
    default: Couldn't find any package by glob 'libxerces-c3.1'
    default: E
    default: : 
    default: Couldn't find any package by regex 'libxerces-c3.1'


解決策
--------
* ``libxerces-c3.2`` を変わりにインストールする

