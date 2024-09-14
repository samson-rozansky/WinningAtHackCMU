//run with node.
//const fetch = require('node-fetch');
import fs from "fs";
import fetch from "node-fetch";

/* token can be found in developer tools > network > messages/typing/search request > Headers > authorization
do NOT share your token with others */
let myToken = fs.readFileSync('myToken.txt', 'utf-8');
/* the server Id and user Id can be found by enabling developer mode in discord,
then right clicking the server's icon and user's name and selecting "Copy ID" */
let serverId = '1275882998591656016';
let channelId = '1275914959858958450';
//choose what you want to name the file that the messages will be copied to here.
let fileToWrite = 'path to location that you want to save the file here (ex: log1.txt)';

let requestUrl = `https://discord.com/api/v9/channels/${channelId}/messages?after=`;
const delay = async (ms = 1000) =>  new Promise(resolve => setTimeout(resolve, ms));
//function to get a channel's name
async function getChannelName(id) {
    return new Promise(async (resolve) => {
        let success = false;
        while (!success) {
            await fetch(`https://discord.com/api/v9/channels/${id}`, {
                method: 'GET',
                headers: {
                    authorization: myToken
                }
            }).then(async (response) => {
                let responseJSON = await response.json();
                if (typeof responseJSON.name != 'undefined') {
                    resolve(responseJSON.name);
                    success = true;
                } else {
                    switch (response.status) {
                        case 429:
                            await delay(2000);
                            break;
                        case 403:
                            resolve("you don't have access to this channel");
                            success = true;
                            break;
                        case 404:
                            resolve("deleted-channel");
                            success = true;
                            break;
                        default:
                            console.log('Error ' + response.status  + ': ' + response.statusText + '. Retrying...');
                            break;
                    }
                }
            });
        }
    });
}
(async ()=> {
    let errorHandler = function(err) {
        if (err) {
            throw err;
        }
    }
    let startTime = Date.now();
    let messagesLogged = 0;
    let thisChannelName = await getChannelName(channelId);
    fs.writeFileSync(fileToWrite,`Messages in channel ${thisChannelName} (id ${channelId})\n\n`, errorHandler);
    //requesting the first batch to get basic info
    await fetch(`https://discord.com/api/v9/guilds/${serverId}/messages/search?channel_id=${channelId}&include_nsfw=true&sort_by=timestamp&sort_order=asc&offset=0`, {
        method: 'GET',
        headers: {
            authorization: myToken
        }
    }).then(async (response) => {
        let responseJSON = await response.json();
        numMessages = responseJSON.total_results;
        if (numMessages == 0) {
            console.log('There are no messages in this channel.');
            return;
        }
        let messageArray1 = responseJSON.messages;
        let numBatches = Math.floor(numMessages / 50) + 1;
        try {
            console.log(`There are ${numBatches} batches of messages.`);
            newMinId = BigInt(messageArray1[0][0].id) - BigInt('1');
            console.log('Each batch has 50 messages, except potentially the last one.');
        } catch (err) {
            console.log('Error ' + response.status  + ': ' + response.statusText);
            throw err;
        }
    //now requesting all the batches
    }).then(async () => {
        let numBatches = Math.floor(numMessages / 50) + 1;
        let previousDelay = false;
        let lastMessageId = '';
        for (let i = 0; i < numBatches; ++i) {
            let success = false;
            if (previousDelay) {
                await delay(2000);
                previousDelay = false;
            }
            while (!success) {
                await fetch(requestUrl.concat(`${newMinId.toString()}&limit=50`), {
                    method: 'GET',
                    headers: {
                        authorization: myToken
                    }
                }).then(async (response) => {
                    let messageArray = await response.json();
                    try {
                        for (let i = messageArray.length - 1; i >= 0; i--) {
                            let message = messageArray[i];
                            let messageSender = message.author.username + '#' + message.author.discriminator + ', id ' + message.author.id;
                            let timeStamp = message.timestamp.substring(0, message.timestamp.indexOf('.')).replace("T", " ");
                            let messageContent = message.content;
                            //replacing mentioned user ids with their actual names
                            for (let mentionedUser of message.mentions) {
                                messageContent = messageContent.replace(`${mentionedUser.id}>`, `${mentionedUser.id}>(${mentionedUser.username}#${mentionedUser.discriminator})`);
                            }
                            //replacing channel ids with their actual names
                            let channelIds = messageContent.match(/<#\d{17,19}>/g);
                            if (channelIds !== null) {
                                for (let id of channelIds) {
                                    id = id.slice(2, -1);
                                    let channelName = await getChannelName(id);
                                    messageContent = messageContent.replace(`${id}>`, `${id}>(${channelName})`);
                                }
                            }
                            messageContent = messageContent.replace(/\n/g, "\n\t");
                            fs.appendFileSync(fileToWrite, messageSender + " at " + timeStamp + ":\n");
                            if (typeof message.sticker_items != 'undefined') {
                                fs.appendFileSync(fileToWrite, `\tsticker: "${message.sticker_items[0].name}"\n`, errorHandler);
                            } else if (messageContent.length != 0) {
                                fs.appendFileSync(fileToWrite, "\t" + messageContent, errorHandler);
                                if (message.edited_timestamp !== null) {
                                    fs.appendFileSync(fileToWrite, ' (edited)', errorHandler);
                                }
                                fs.appendFileSync(fileToWrite, "\n", errorHandler);
                            }
                            if (message.attachments.length != 0) {
                                fs.appendFileSync(fileToWrite, '\tattachments: ', errorHandler);
                                for (let i = 0; i < message.attachments.length - 2; ++i) {
                                    fs.appendFileSync(fileToWrite, message.attachments[i].url + ', ', errorHandler);
                                }
                                fs.appendFileSync(fileToWrite, message.attachments[message.attachments.length - 1].url + '\n', errorHandler);
                            }
                            fs.appendFileSync(fileToWrite, '\n', errorHandler);
                        }
                        lastMessageId = messageArray[0].id;
                        console.log(`Batch ${i + 1} added.`);
                        messagesLogged += messageArray.length;
                        success = true;
                    } catch (err) {
                        if (messageArray.length == 0) {
                            i = numBatches;
                            success = true;
                        } else {
                            console.log('Error ' + response.status  + ': ' + response.statusText + '. Retrying...');
                            if (response.status == 429) {
                                await delay(2000);
                                previousDelay = true;
                            } else {
                                console.log(response);
                            }
                        }
                    }
                });
            }
            newMinId = BigInt(lastMessageId) + BigInt('1');
        }
        console.log('Finished! '+ messagesLogged + ' messages were logged to ' + fileToWrite + '.');
        let timeElapsed = (Date.now() - startTime) / 60000;
        let numMinutes = Math.floor(timeElapsed);
        let numSeconds = ((timeElapsed - numMinutes) * 60).toFixed(1);
        console.log('It took ' + numMinutes + ' minutes and ' + numSeconds + ' seconds to retrieve the messages.');
    });
})();
