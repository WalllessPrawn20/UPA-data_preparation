ZIP_NAME = xmelchm00.zip

FILES =	build.sh \
        run.sh \
        scrape_data.py \
        scrape_url.py \
        urls.txt \
        data.tsv

.PHONY: all zip clean

all: zip

zip:
	zip $(ZIP_NAME) $(FILES)

clean:
	rm -f $(ZIP_NAME)