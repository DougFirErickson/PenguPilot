/*___________________________________________________
 |  _____                       _____ _ _       _    |
 | |  __ \                     |  __ (_) |     | |   |
 | | |__) |__ _ __   __ _ _   _| |__) || | ___ | |_  |
 | |  ___/ _ \ '_ \ / _` | | | |  ___/ | |/ _ \| __| |
 | | |  |  __/ | | | (_| | |_| | |   | | | (_) | |_  |
 | |_|   \___|_| |_|\__, |\__,_|_|   |_|_|\___/ \__| |
 |                   __/ |                           |
 |  GNU/Linux based |___/  Multi-Rotor UAV Autopilot |
 |___________________________________________________|
  
 Drotek MPU9150 + MS5611 Driver Interface

 Copyright (C) 2014 Jan Roemisch, Integrated Communication Systems Group, TU Ilmenau
 Copyright (C) 2014 Tobias Simon, Integrated Communication Systems Group, TU Ilmenau

 This program is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 2 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details. */



#ifndef __DROTEK_9150_H__
#define __DROTEK_9150_H__


#include "../sensors/util/marg_data.h"
#include "../sensors/mpu6050/mpu6050.h"


typedef struct
{
   mpu6050_t mpu;
}
drotek_9150_t;


int drotek_9150_init(drotek_9150_t *drotek, i2c_bus_t *bus);

int drotek_9150_read(marg_data_t *data, drotek_9150_t *drotek);


#endif /* __DROTEK_9150_H__ */

