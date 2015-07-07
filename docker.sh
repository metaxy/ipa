docker stop ipa_server
docker build -t ipa .
docker rm ipa_server
docker run --name ipa_server -i -d -p 8123:8080 ipa


