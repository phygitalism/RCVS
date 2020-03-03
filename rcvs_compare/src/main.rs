use rayon::prelude::*;
use std::collections::HashSet;
use std::fs;
use std::io::{self, BufRead, BufReader, Read};

//Creates Vector from file
fn read(io: impl Read) -> io::Result<Vec<Vec<f64>>> {
    let br = BufReader::new(io);
    br.lines()
        .map(|line| {
            line.map(|line| {
                line.split_whitespace()
                    .map(|x| x.parse().unwrap_or(-1.0))
                    .collect()
            })
        })
        .collect()
}

//Compares two objects
fn compare(one: &[Vec<f64>], two: &[Vec<f64>], error: f64) -> f64 {
    // assert_eq!(one.len(), two.len());
    assert!(one.len() <= two.len());

    let length = one.len();
    let mut count = 0.0;
    let mut seen = HashSet::new();

    for orig in one {
        let size = orig.len();
        let min_similarity = (1.0 - error) * size as f64;

        let chosen = two.iter()
            .enumerate()
            .filter(|&(i, _)| !seen.contains(&i))
            .find_map(|(i, targ)| {
                let similarity = orig.iter()
                    .zip(targ)
                    .map(|(&x, &y)| 1.0 - (x - y).abs())
                    .sum::<f64>();

                if similarity < min_similarity {
                    None
                } else {
                    Some((i, similarity))
                }
            });

        if let Some((i, similarity)) = chosen {
            count += similarity / size as f64;
            seen.insert(i);
        }
    }
    count / length as f64
}

//Compares one object with others on different threads
fn one_with_others(
    obj: &[Vec<f64>],
    dict: &[(String, Vec<Vec<f64>>)],
) -> Vec<(usize, f64)> {
    let length = dict.len();

    dict.into_par_iter()
        .map(|x| &x.1)
        .enumerate()
        .map(|(i, row)| {
            println!("Puny human is instructed to wait.. {}/{}", i + 1, length);
            (i, compare(obj, row, 0.01))
        })
        .collect()
}

fn main() {
    let ray = 1280; //name of directory
    let obj_cur = "Suzanne_lo"; //name of object

    let mut objects = Vec::new();
    let path_rays = format!("./rays/{}/", ray);
    let paths = fs::read_dir(path_rays).unwrap();

    let obj_path = format!("./rays/{}/{}", ray, obj_cur);
    let obj = (
        obj_cur.to_string(),
        read(fs::File::open(obj_path).unwrap()).unwrap(),
    );

    for path in paths {
        let path = path.unwrap();
        let name = path.file_name();
        objects.push((
            name.to_string_lossy().into_owned(),
            read(fs::File::open(path.path()).unwrap()).unwrap(),
        ));
    }

    let mut result = one_with_others(&obj.1, &objects);
    result.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap());
    print!("{}\n", "_".repeat(200));
    println!("{}", obj.0);
    for (idx, similarity) in result {
        let percent = (similarity * 100.0).round() as usize;
        println!(
            "{:>36} |{:<100}| {:<14}",
            objects[idx].0,
            "▮".repeat(percent),
            similarity
        );
    }
}
