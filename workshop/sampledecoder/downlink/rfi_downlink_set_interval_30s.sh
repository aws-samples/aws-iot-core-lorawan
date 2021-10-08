# The interval timer is contained in byte 2 and 3 of the message. The two bytes form a 16-bit integer 
# and can have a value between 30 and 3600 seconds (0x1E to 0xE10 in hex). Any value outside of 
# this range will be ignored. 
 
# When the RPSW receives a type F0 message with the correct number of seconds it sends a reply 
# with the same message to confirm. When the interval timer value is in the correct range i.e., between 
# 30 and 3600, the reply message contains the new value. However, when the interval timer contains 
# an incorrect value i.e., outside the 30 to 3600 range the reply contains the original value that was 
# already stored in the RPSW. 
 
# You can request the current value of the interval setting by sending an empty type F0 message. 
 
# For example, to set the reporting interval to 60 seconds (0x3C hex) you have to send the following 
# message: 
#  F0003C 
 
# The RPSW will reply with: 
 
#  F0003C 
 
# When you want to find out what the reporting interval is you would send: 
 
#  F0 
 
# The RPSW will reply with: 
 
#  F0003C 
# 60 = F0 = 8A==
# 30 = 1E = Hg==
# F0003C = 8AA8
# F0001E = 8AAe
aws iotwireless send-data-to-wireless-device \
                    --id 978ea3fa-5448-4d0b-990c-19a0b45d86a3 \
                    --transmit-mode 1 \
                    --payload-data 8AAe \
                    --wireless-metadata LoRaWAN={FPort=1}